# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2022-05-04 19:55:32
@LastEditors  : xupingmao
@LastEditTime : 2023-09-29 15:31:55
@FilePath     : /xnote/xutils/db/binlog.py
@Description  : 数据库的binlog,用于同步
"""
import threading
import logging
import typing

from typing import Optional
from web import Storage
from xutils.base import BaseDataRecord
from xutils.interfaces import SQLDBInterface
from xutils import jsonutil, dateutil

class BinLogOpType:
    """binlog操作枚举"""
    put = "put"
    delete = "delete"
    file_upload = "file_upload"
    file_delete = "file_delete"
    file_rename = "file_rename"
    sql_upsert = "sql_upsert"
    sql_delete = "sql_delete"

class BinLogKeyType:
    INT = 1
    STR = 2

    @classmethod
    def get_type(cls, key: typing.Union[str, int]):
        if isinstance(key, str):
            return cls.STR
        if isinstance(key, int):
            return cls.INT
        raise Exception(f"unknown type {type(key)}")
    
    @classmethod
    def get_value(cls, key_type: int, record_key: str):
        if key_type == cls.INT:
            return int(record_key)
        return record_key

class FileLog(Storage):
    """文件变更日志"""
    def __init__(self):
        self.fpath = ""
        self.ftype = ""
        self.user_name = ""
        self.user_id = 0
        self.webpath = ""
        self.old_webpath = ""
        self.mtime = 0.0

class BinLogRecord(BaseDataRecord):
    _ignore_save_fields = set(["old_value", "binlog_id", "value_obj", "key_obj"])

    def __init__(self, **kw):
        self.create_time = dateutil.timestamp_ms()
        self.op_type = "" # see BinLogOpType
        self.key_type = 0 # 主键类型
        self.record_key = "" # type: str
        self.record_value = "" # type: str
        self.table_name = ""
        self.binlog_id = 0
        self.value_obj = None # type: object # 虚拟字段
        self.old_value = None
        super().__init__(**kw)

    def build(self):
        if self.key_type == 0:
            self.key_type = BinLogKeyType.get_type(self.record_key)

    @property
    def key_obj(self):
        return BinLogKeyType.get_value(self.key_type, self.record_key)

class BinLog:
    _lock = threading.RLock()
    _delete_lock = threading.RLock()
    _instance = None
    _is_enabled = False
    _max_size = 10000
    log_debug = False
    logger = logging.getLogger("binlog")
    record_old_value = False
    db: SQLDBInterface

    def __init__(self) -> None:
        """正常要使用单例模式使用"""
        with self._lock:
            if self._instance != None:
                raise Exception("只能创建一个BinLog单例")
            self._instance = self
        
    @classmethod
    def init(cls, db: SQLDBInterface):
        cls.db = db

    @property
    def last_seq(self):
        return self.find_last_seq()

    @classmethod
    def get_instance(cls):
        # type: () -> BinLog
        if cls._instance != None:
            return cls._instance

        with cls._lock:
            if cls._instance == None:
                cls._instance = BinLog()
            return cls._instance

    @classmethod
    def set_enabled(cls, is_enabled):
        cls._is_enabled = is_enabled

    @classmethod
    def set_max_size(cls, max_size):
        cls._max_size = max_size

    def count_size(self):
        return self.db.count()
    
    def get_last_log(self):
        last_log = self.db.select_first(order="binlog_id desc")
        return BinLogRecord.from_dict_or_None(last_log)

    def find_last_seq(self):
        last_log = self.get_last_log()
        if last_log:
            return last_log.binlog_id
        return 0

    def find_start_seq(self):
        record = self.db.select_first(order="binlog_id")
        if record is None:
            return 0
        return BinLogRecord.from_dict(record).binlog_id
    
    def get_max_id(self):
        return self.find_last_seq()

    def add_log(self, optype: str, key: typing.Union[str, int], value=None, batch=None, old_value=None, *, 
                record_value=False, table_name: Optional[str]=None):
        if not self._is_enabled:
            return

        # 获取自增ID操作是并发安全的, 所以这里不需要加锁, 加锁过多不仅会导致性能下降, 还可能引发死锁问题
        binlog_body = BinLogRecord()
        binlog_body.op_type = optype
        binlog_body.record_key = str(key)
        binlog_body.key_type = BinLogKeyType.get_type(key)

        if self.record_old_value and old_value != None:
            binlog_body.old_value = old_value
        
        if record_value and value != None:
            binlog_body.record_value = jsonutil.tojson(value)
        
        if table_name != None:
            binlog_body.table_name = table_name
        
        self.db.insert(**binlog_body.to_save_dict())

    def list(self, start_binlog_id=0, limit=10):
        """从start_binlog_id开始查询limit个binlog"""
        results = self.db.select(where="binlog_id>=$start_binlog_id", 
                                 order="binlog_id",limit=limit,
                                 vars=dict(start_binlog_id=start_binlog_id))
        return BinLogRecord.from_dict_list(results)
    
    def raw_list(self, offset=0, limit=20, order="binlog_id"):
        """原生的查询接口"""
        results = self.db.select(order=order,limit=limit,offset=offset)
        return BinLogRecord.from_dict_list(results)

    def delete_expired(self):
        assert self._max_size != None, "binlog_max_size未设置"
        assert self._max_size > 0, "binlog_max_size必须大于0"

        size = self.count_size()
        self.logger.info("count size:%s", size)
        max_id = self.get_max_id()
        min_keep_id = max_id - self._max_size + 1
        batch_size = 100
        
        logging.info("max_id:%s, min_keep_id:%s", max_id, min_keep_id)

        if min_keep_id > 0:
            with self._delete_lock:
                self.logger.info("limit size: %s", batch_size)
                delete_rows = self.db.select(what="binlog_id", where="binlog_id<$min_keep_id", 
                                             limit=batch_size, vars=dict(min_keep_id=min_keep_id))
                delete_ids = [row.binlog_id for row in delete_rows]
                self.db.delete(where="binlog_id IN $id_list", vars=dict(id_list=delete_ids))

