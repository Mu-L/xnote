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

def do_upgrade():
    # since v2.9.9
    base.execute_upgrade("20251108_system_meta", fix_system_meta)

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


def fix_system_meta():
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
        