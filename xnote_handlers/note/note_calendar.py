# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2020/12/17 23:18:20
# @modified 2020/12/17 23:25:30

import typing
import xutils

from xutils import Storage
from xnote.core import xmanager
from xnote.core import xauth
from xnote.core import xtemplate
from xnote.plugin import TabBox
from datetime import date, timedelta, datetime
from xutils import dateutil
from xutils import textutil
from xnote_handlers.note import dao as note_dao
from xnote_handlers.note.dao_read import list_updated_notes, list_created_notes
from xnote.core.xnote_user_config import UserConfig
from xnote_handlers.plan.dao import MonthPlanDao
from xnote_handlers.config import LinkConfig

class CalendarCell:
    def __init__(self, date_number="", month = 0, date_info = "", css_class=""):
        self.date_number = date_number
        self.date_info = date_info
        self.month = month
        self.css_class = css_class

class CalendarRow(list):
    def is_valid(self, cur_month: int):
        for cell in self:
            cell: CalendarCell
            if cell.month == cur_month:
                return True
        return False


HOLIDAY_MAP = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-05": "惊蛰",
    "03-08": "妇女节",
    "03-20": "春分",
    "04-01": "愚人节",
    "05-01": "劳动节",
    "05-04": "青年节",
    "06-01": "儿童节",
    "09-03": "抗战胜利日",
    "09-10": "教师节",
    "10-01": "国庆节"
}

class NoteCalendarHandler:
    """日历视图"""

    @xauth.login_required()
    def GET(self):
        user = xauth.current_name_str()
        tab = xutils.get_argument_str("tab", "note_create")
        xmanager.add_visit_log(user, "/note/calendar")

        today = datetime.now().date()
        today_str = today.strftime("%Y-%m")
        date_str = xutils.get_argument_str("date", today_str)
        date_obj = dateutil.parse_date_to_object(date_str)
        start_date = date(year=date_obj.year, month=date_obj.month, day=1)
        user_id = xauth.current_user_id()

        kw = Storage()
        self.handle_toolbar_tab(kw, user_id=user_id)

        user_info = xauth.current_user()
        assert user_info != None
        
        kw.plan_record = MonthPlanDao.get_or_create(user_info, date_str, fill_notes_info=True)
        kw.events_tab = self.get_tab()
        kw.calendar_heads = self.get_heads()
        kw.calendar_rows = self.get_rows(start_date=start_date)
        
        if tab == "note_create":
            kw.created_notes = list_created_notes(creator_id=user_id, year=date_obj.year, month=date_obj.month)
        if tab == "note_update":
            kw.updated_notes = list_updated_notes(creator_id=user_id, year=date_obj.year, month=date_obj.month)
        
        kw.year = date_obj.year
        kw.month = date_obj.month
        kw.date_str = date_str
        kw.tab = tab
        kw.title = "日历"
        kw.parent_link = LinkConfig.app_index
        kw.right_link = LinkConfig.calendar
        kw.right_link2 = LinkConfig.create_note

        return xtemplate.render("note/page/note_calendar.html", **kw)

    def handle_toolbar_tab(self, kw, user_id: int):
        default_value = UserConfig.calendar_toolbar_tab.get_str(user_id=user_id)

        tab = TabBox(tab_key="toolbar_tab", tab_default=default_value)
        tab.add_item(title="展示日历", value="calendar")
        tab.add_item(title="隐藏日历", value="none")
        
        toolbar_tab = xutils.get_argument_str("toolbar_tab", default_value)
        if default_value != toolbar_tab:
            UserConfig.calendar_toolbar_tab.save_config(user_id, toolbar_tab)

        kw.toolbar_tab = tab
        kw.show_calendar = toolbar_tab == "calendar"
    
    def get_tab(self):
        tab = TabBox(tab_key="tab", tab_default="note_create")
        tab.add_item(title="笔记创建", value="note_create")
        tab.add_item(title="笔记更新", value="note_update")
        tab.add_item(title="随手记", value="message")
        return tab
    
    def get_heads(self):
        result: typing.List[CalendarCell] = []
        for date_info in "一二三四五六日":
            result.append(CalendarCell(date_info=date_info))
        return result

    def get_rows(self, start_date: date):
        today = datetime.now().date()
        cur_month = start_date.month
        start_date = start_date - timedelta(days=6)
        cur_date = start_date
        while cur_date.weekday() != 0:
            cur_date += timedelta(days=1)
        
        result: typing.List[CalendarRow] = []
        row = CalendarRow()
        for x in range(100):
            date_info = ""
            css_class = "currentMonth"
            if cur_date.month != cur_month:
                css_class = "otherMonth"
            if cur_date == today:
                css_class += " currentDay"
                date_info = "今天"
            holiday = HOLIDAY_MAP.get(cur_date.strftime("%m-%d"), "")
            date_info = textutil.append_text(date_info, holiday)
            row.append(CalendarCell(str(cur_date.day), month=cur_date.month, css_class=css_class, date_info=date_info))
            cur_date += timedelta(days=1)

            if len(row) >= 7:
                if not row.is_valid(cur_month=cur_month):
                    break
                result.append(row)
                row = CalendarRow()
        
        return result





xurls = (
    r"/note/calendar", NoteCalendarHandler,
)

