# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2025-11-08
@LastEditors  : xupingmao
@LastEditTime : 2024-08-31 23:02:30
@FilePath     : /xnote/xnote_migrate/upgrade_021.py
@Description  : 描述
"""
import logging
import xutils

from . import base
from xutils.base import BaseDataRecord
from xnote.core import xtables
from xnote.core.xtables import DEFAULT_DATETIME
from xutils import dateutil
from xutils import dbutil
from xnote.core import xauth

def do_upgrade():
    # since v2.9.9
    base.execute_upgrade("20251108_system_meta", migrate_system_meta)
    base.execute_upgrade("20251108_user_meta", migrate_user_meta)

class SystemInfoRecord(BaseDataRecord):
    def __init__(self, **kw):
        self.id = 0
        self.ctime = DEFAULT_DATETIME
        self.mtime = DEFAULT_DATETIME
        self.info_key = ""
        self.info_value = ""
        self.version = 0
        self.update(kw)

class SystemMetaRecord(BaseDataRecord):
    def __init__(self):
        self.id = 0
        self.create_time = 0
        self.update_time = 0
        self.meta_key = ""
        self.meta_value = ""
        self.version = 0

class UserMetaRecord(BaseDataRecord):
    def __init__(self):
        self.id = 0
        self.create_time = 0
        self.update_time = 0
        self.user_id = 0
        self.meta_key = ""
        self.meta_value = ""
        self.version = 0

def migrate_system_meta():
    old_db = xtables.get_table_by_name("system_info")
    new_db = xtables.get_table_by_name("system_meta")
    for item in old_db.iter():
        info = SystemInfoRecord.from_dict(item)
        new_item = SystemMetaRecord()
        new_item.id = info.id
        new_item.create_time = int(dateutil.parse_datetime(info.ctime) * 1000)
        new_item.update_time = int(dateutil.parse_datetime(info.mtime) * 1000)
        new_item.meta_key = info.info_key
        new_item.meta_value = info.info_value
        new_item.version = info.version
        new_db.replace(**new_item)
        
def migrate_user_meta():
    old_db = dbutil.get_hash_table("user_config")
    new_db = xtables.get_table_by_name("user_meta")
    for origin_key, value in old_db.iter(limit=-1):
        user_name, config_key = origin_key.split(":")
        user_id = xauth.UserDao.get_id_by_name(user_name)
        meta_record = UserMetaRecord()
        meta_record.user_id = user_id
        meta_record.create_time = dateutil.timestamp_ms()
        meta_record.update_time = dateutil.timestamp_ms()
        meta_record.meta_key = config_key
        meta_record.meta_value = str(value)
        meta_record.pop("id", None)
        new_db.replace(**meta_record)
