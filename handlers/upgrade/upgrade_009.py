# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2022-07-03 09:03:21
@LastEditors  : xupingmao
@LastEditTime : 2022-12-10 16:53:56
@FilePath     : /xnote/handlers/upgrade/upgrade_009.py
@Description  : 描述
"""
from xutils import dbutil
from handlers.upgrade.upgrade_main import is_upgrade_done
from handlers.upgrade.upgrade_main import mark_upgrade_done
from handlers.note.dao import add_history_index

def do_upgrade():
    upgrade_key = "upgrade_009"
    if is_upgrade_done(upgrade_key):
        return
    
    db = dbutil.get_hash_table("note_history")

    for key, value in db.iter(limit=-1):
        note_id, version = key.split(":")
        add_history_index(note_id, value.version, value)
    
    mark_upgrade_done(upgrade_key)

