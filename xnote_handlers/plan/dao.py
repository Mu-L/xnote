# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2023-02-12 00:00:00
@LastEditors  : xupingmao
@LastEditTime : 2023-06-24 10:10:33
@FilePath     : /xnote/handlers/plan/dao.py
@Description  : 计划管理
"""
import time

from typing import Union, List
from xnote.core import xauth
from xutils import dbutil, Storage
from xutils import BaseDataRecord
from xnote_handlers.note.models import NoteIndexDO

class MonthPlanRecord(BaseDataRecord):
    _ignore_save_fields = ["notes", "create_notes", "update_notes"]

    def __init__(self, **kw):
        self._id = ""
        self.user = ""
        self.user_id = 0
        self.month = ""
        self.notes: List[NoteIndexDO] = [] # stared note ids details
        self.note_ids = [] # stared note ids
        self.create_notes: List[NoteIndexDO] = []
        self.update_notes: List[NoteIndexDO] = []
        self.update(kw)
    
    def save(self):
        MonthPlanDao.update(self)

class MonthPlanDao:

    db = dbutil.get_table_v2("month_plan")

    @classmethod
    def get_or_create(cls, user_info: xauth.UserDO, month = "2020-03", fill_notes_info = False):
        db = cls.db
        if month == "now":
            month = time.strftime("%Y-%m")
        user_id = user_info.user_id
        user_name = user_info.name

        db_record = db.select_first(where = dict(user_id=user_id, month = month))
        if db_record == None:
            record = MonthPlanRecord()
            record.user_id = user_id
            record.user = user_name
            record.month = month
            new_id = db.insert(record.to_save_dict())
            record = cls.get_by_id(user_id=user_id, plan_id=new_id)
        else:
            record = MonthPlanRecord.from_dict(db_record)
        
        if record is None:
            raise Exception("plan record is None")

        if fill_notes_info and len(record.note_ids) > 0:
            from xnote_handlers.note import dao as note_dao
            note_ids = list(filter(lambda x:x!="", record.note_ids))
            record.notes = note_dao.batch_query_list(note_ids)
            record.notes.sort(key = lambda x:x.name)

        return record

    @classmethod
    def get_by_id(cls, user_id = 0, plan_id: Union[str, int] = ""):
        db = cls.db
        record = db.get_by_id(plan_id)
        if record == None:
            return None
        result = MonthPlanRecord(**record)
        if result.user_id != user_id:
            return None
        return result
    
    @classmethod
    def get_by_month(cls, user_id = 0, month = "2020-03"):
        db = cls.db
        record = db.select_first(where = dict(user_id=user_id, month = month))
        if record == None:
            return None
        return MonthPlanRecord(**record)
    
    @classmethod
    def update(cls, record: MonthPlanRecord):
        dict_values = record.to_save_dict()
        return cls.db.update(dict_values)
