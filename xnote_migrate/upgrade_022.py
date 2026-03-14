# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2026-03-14
"""
import logging
import xutils
from xnote.core import xtables
from xnote.core import xauth
from xnote.core import xnote_event
from xnote_handlers.note.dao import NoteIndexDao
from xnote.service.tag_service import NoteTagBindService, NoteTagInfoService
from . import base


def do_upgrade():
    base.execute_upgrade("20260314_note_sys_tags", update_note_system_tags)

_mappings = {
    "$todo$": "_todo",
    "$1$": "_important",
    "$file$": "_file",
    "$link$": "_link",
    "$book$": "_book",
    "$people$": "_people",
    "$phone$": "_phone"
}
     
     
def update_note_system_tags():   
    for user in xauth.UserDao.iter():
        user_id = user.user_id
            
        for old_tag, new_tag in _mappings.items():
            tag_binds = NoteTagBindService.list_by_tag(user_id=user_id, tag_code=old_tag, limit=1000)
            for tag_bind in tag_binds:
                note_id = tag_bind.target_id
                old_tags = NoteTagBindService.get_tag_codes(user_id=user_id, target_id=note_id)
                new_tags = [_mappings.get(tag, tag) for tag in old_tags]
                NoteTagBindService.bind_tags(user_id=user_id, target_id=note_id, tags=new_tags, update_only_changed=True)
                NoteIndexDao.update_tags(note_id=note_id, tags = new_tags)
        
            NoteTagInfoService.rename(user_id=user_id, old_tag_code=old_tag, new_tag_code=new_tag)
            
