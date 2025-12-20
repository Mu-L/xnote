# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2023-02-12 00:00:00
@LastEditors  : xupingmao
@LastEditTime : 2023-11-05 22:54:32
@FilePath     : /xnote/handlers/plan/plan.py
@Description  : 计划管理
"""
import xutils
import datetime

from xnote.core import xauth, xtemplate
from xutils import Storage
from xnote_handlers.plan.dao import MonthPlanDao
from xnote_handlers.note import dao as note_dao
from xutils import functions, dateutil
from xutils import webutil
from xnote_handlers.note.dao_read import list_updated_notes, list_created_notes

class MonthPlanHandler:

    @xauth.login_required()
    def GET(self):
        kw = Storage()
        user_info = xauth.current_user()
        assert user_info != None
        
        date = xutils.get_argument_str("date", "now")
        date = date.replace("/", "-")
        record = MonthPlanDao.get_or_create(user_info, date, fill_notes_info=True)

        year, month = record.month.split("-")
        int_year = int(year)
        int_month = int(month)
        user_id = user_info.id

        kw.plan_record = record
        kw.year = int_year
        kw.month = int_month
        kw.created_notes = list_created_notes(creator_id=user_id, year=int_year, month=int_month)
        kw.updated_notes = list_updated_notes(creator_id=user_id, year=int_year, month=int_month)

        return xtemplate.render("plan/page/month_plan.html", **kw)

class MonthPlanAddAjaxHandler:
    @xauth.login_required()
    def POST(self):
        plan_id = xutils.get_argument_str("plan_id")
        note_ids_str = xutils.get_argument_str("note_ids", "")
        note_ids = note_ids_str.split(",")
        if plan_id == "":
            return webutil.FailedResult(code="400", message="参数id不能为空")

        user_id = xauth.current_user_id()
        record = MonthPlanDao.get_by_id(user_id, plan_id)
        if record != None:
            assert isinstance(note_ids, list)
            for id in note_ids:
                if id not in record.note_ids:
                    record.note_ids.append(id)
            record.save()
            return webutil.SuccessResult()
        else:
            return webutil.FailedResult(code="500", message="计划不存在")

class MonthPlanRemoveAjaxHandler:
    @xauth.login_required()
    def POST(self):
        id = xutils.get_argument_str("id", "")
        note_id = xutils.get_argument_str("note_id", "")
        if id == "":
            return webutil.FailedResult(code="400", message="参数id不能为空")
        if note_id == "":
            return webutil.FailedResult(code="400", message="参数note_id不能为空")

        user_id = xauth.current_user_id()
        record = MonthPlanDao.get_by_id(user_id, id)
        if record != None:
            functions.listremove(record.note_ids, note_id)
            record.save()
            return webutil.SuccessResult()
        else:
            return webutil.FailedResult(code="500", message="计划不存在")

xurls = (
    r"/plan/month", MonthPlanHandler,
    r"/plan/month/add", MonthPlanAddAjaxHandler,
    r"/plan/month/remove", MonthPlanRemoveAjaxHandler,
)