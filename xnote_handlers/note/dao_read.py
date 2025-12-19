# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2022-07-14 22:51:33
@LastEditors  : xupingmao
@LastEditTime : 2023-01-28 23:08:03
@FilePath     : /xnote/handlers/note/dao_read.py
@Description  : 读操作
"""
import xutils

from datetime import datetime
from xnote_handlers.note import dao as note_dao
from xnote_handlers.note.dao import list_by_parent, NoteIndexDO
from xutils import Storage
from xutils import dateutil

def get_note_depth(note: NoteIndexDO, max_recursive=10):
    # type: (Storage, int) -> int
    """计算笔记的深度"""
    assert note != None
    assert note.type == "group"

    if max_recursive <= 0:
        return 0

    max_depth = 1

    for item in list_by_parent(note.creator, parent_id = note.id):
        if item.type == "group":
            depth = get_note_depth(item, max_recursive-1)
            max_depth = max(max_depth, depth+1)
            
    return max_depth

def list_created_notes(creator_id=0, year=0, month=0):
    next_year = year
    next_month = month + 1
    if next_month == 13:
        next_year += 1
        next_month = 1

    date_start = datetime(year=year, month=month, day=1)
    date_end = datetime(year=next_year, month=next_month, day=1)
    return note_dao.NoteIndexDao.list(
        creator_id=creator_id, 
        date_start=dateutil.format_datetime(date_start), 
        date_end=dateutil.format_datetime(date_end))


def list_updated_notes(creator_id=0, year=0, month=0):
    history_list = note_dao.NoteHistoryIndexDao.list_by_month(creator_id=creator_id, year = year, month=month)
    result_dict = {} # type: dict[int, note_dao.NoteHistoryIndexDO]
    for item in history_list:
        old_item = result_dict.get(item.note_id)
        if old_item is None:
            result_dict[item.note_id] = item
        elif item.mtime > old_item.mtime:
            result_dict[item.note_id] = item
    result = sorted(result_dict.values(), key = lambda x:x.mtime, reverse=True)
    id_list = [x.note_id for x in history_list]
    note_dict = note_dao.batch_query_dict(id_list=id_list)
    note_list = []
    for item in result:
        note_index = note_dict.get(item.note_id)
        if note_index != None:
            note_list.append(note_index)
            note_index.badge_info = item.badge_info
    return note_list
