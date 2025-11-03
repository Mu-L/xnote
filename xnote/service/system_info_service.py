import logging
import typing

from xnote.core import xtables, xconfig
from xutils import BaseDataRecord
from xutils import DEFAULT_DATETIME
from xutils import dateutil
from web.db import SQLLiteral
from xutils import BaseEnum, EnumItem
from xutils.cacheutil import LocalCacheObject

class SystemInfoRecord(BaseDataRecord):
    def __init__(self, **kw):
        self.id = 0
        self.ctime = DEFAULT_DATETIME
        self.mtime = DEFAULT_DATETIME
        self.info_key = ""
        self.info_value = ""
        self.version = 0
        self.update(kw)

    def to_save_dict(self):
        result = dict(**self)
        result.pop("id", None)
        return result


class SystemInfoService:

    # TODO 加上缓存封装
    db = xtables.get_table("system_info")

    @classmethod
    def save_info(cls, info_key: str, info_value: str):
        now = dateutil.format_datetime()
        rowcount = int(cls.db.update(where=dict(info_key=info_key), mtime = now, info_value=info_value, version = SQLLiteral("version+1")))
        if rowcount > 0:
            return
        record = SystemInfoRecord()
        record.info_key = info_key
        record.info_value = info_value
        record.ctime = dateutil.format_datetime()
        record.mtime = dateutil.format_datetime()
        cls.db.insert(**record.to_save_dict())

    @classmethod
    def get_info(cls, info_key: str):
        record = cls.db.select_first(where = dict(info_key = info_key))
        return SystemInfoRecord.from_dict_or_None(record)

    @classmethod
    def get_info_value(cls, info_key: str):
        info = cls.get_info(info_key)
        if info:
            return info.info_value
        return None

class SystemInfoEnumItem:

    def __init__(self, info_name="", info_key="", default_value=""):
        super().__init__()
        self.info_name = info_name
        self.info_key = info_key
        self.default_value = default_value
        def load_func():
            logging.info("load info value, info_key=%s", info_key)
            return SystemInfoService.get_info_value(info_key=info_key)
        self._cache = LocalCacheObject(expire_seconds=60, load_func=load_func)

    @property
    def value(self):
        return self.info_value
    
    def save_info(self, info_value: str):
        result = SystemInfoService.save_info(self.info_key, info_value)
        self._cache.expire()
        return result
    
    @property
    def bool_value(self):
        value = self.value
        return value in ("1", "true")
    
    @property
    def info_value(self):
        cache_value = self._cache.get()
        if cache_value != None:
            return cache_value
        return self.default_value
    
    @property
    def info_value_int(self):
        if self.info_value == "":
            return 0
        return int(self.info_value)
    
    def expire_cache(self):
        self._cache.expire()

class SystemInfoEnum:
    # 运行状态
    db_backup_file = SystemInfoEnumItem("数据库备份文件", "db.backup.file")
    db_backup_count = SystemInfoEnumItem("数据总量", "db.backup.rows")

    # 配置信息
    trace_malloc_enabled = SystemInfoEnumItem("trace_malloc开关", "config.trace_malloc.enabled")
    page_size = SystemInfoEnumItem("分页大小", "config.page_size.int")
    trash_expire_seconds = SystemInfoEnumItem("回收站清理周期", "config.trash_expire.seconds", default_value=str(3600*24*30))
    fs_hide_files = SystemInfoEnumItem("隐藏系统文件", "config.fs.hide_files.bool")
    debug_html_box = SystemInfoEnumItem("调试HTML盒模型", "config.debug_html_box.bool")
    dev_mode = SystemInfoEnumItem("开发者模式", "config.dev_mode.bool")
    init_script = SystemInfoEnumItem("启动脚本", "config.init.script")

    @classmethod
    def init(cls):
        items: typing.List[SystemInfoEnumItem] = []
        for value in cls.__dict__.values():
            if isinstance(value, SystemInfoEnumItem):
                items.append(value)
        cls._items = items

    @classmethod
    def get_by_info_key(cls, info_key: str):
        for item in cls._items:
            if item.info_key == info_key:
                return item
        return None

SystemInfoEnum.init()
xconfig.DEBUG_HTML_BOX = SystemInfoEnum.debug_html_box._cache
xconfig.DEV_MODE = SystemInfoEnum.dev_mode._cache
