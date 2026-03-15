import xutils
from xnote.core import xauth
from xnote.plugin import DataTable, TableActionType, Card, ActionBar, EditFormButton
from .models import NoteViewContext
from .dao_fragment import NoteFragmentDao, NoteFragmentRecord
from .dao import NoteIndexDao
from xnote.plugin.table_plugin import BaseTablePlugin
from xutils.base import Storage
from xutils import webutil, dateutil

def render_note_fragment(ctx: NoteViewContext):
    if ctx.tab != "" and ctx.tab != "all":
        return
    
    note_id = ctx.note_id
    
    table = DataTable()
    table.add_head("时间", "date_text")
    table.add_head("描述", "content")
    table.add_action(title="编辑", type=TableActionType.edit_form, link_field="edit_url")
    table.add_action(title="删除", type=TableActionType.confirm, link_field="delete_url", 
                        msg_field="delete_msg", css_class="btn danger")


    fragments = NoteFragmentDao.list_by_note_id(note_id=note_id)
    for item in fragments:
        item["edit_url"] = f"/note/fragment?action=edit&note_id={note_id}&frag_id={item.frag_id}"
        item["delete_url"] = f"/note/fragment?action=delete&frag_id={item.frag_id}"
        item["delete_msg"] = f"确认删除事件【{item.content}】吗"
        table.add_row(item)
    
    card = Card()
    action_bar = ActionBar()
    action_bar.add_span("事件时间线", css_class="bold card-title-span btn-line-height", id="events-timeline")
    action_bar.add_edit_button(text="新增事件", url=f"/note/fragment?action=edit&note_id={note_id}", float_right=True, css_class="btn-default")
    
    card.add(action_bar)
    card.add(table)
    ctx.note_fragment = card


class FragmentHandler(BaseTablePlugin):
    require_admin = False
    require_login = True
    
    def handle_edit(self):
        frag_id = xutils.get_argument_int("frag_id")
        note_id = xutils.get_argument_int("note_id")
        user_id = xauth.current_user_id()
        
        if frag_id > 0:
            frag_record = NoteFragmentDao.get_by_frag_id(frag_id=frag_id, user_id=user_id)
        else:
            frag_record = NoteFragmentRecord()
            frag_record.note_id = note_id
            frag_record.date_text = dateutil.format_date()

        if frag_record is None:
            return "无效的记录"
        
        form = self.create_form()
        form.path = "/note/fragment"
        form.add_row("片段ID", "frag_id", css_class="hide", value=str(frag_id))
        form.add_row("笔记ID", "note_id", readonly=True, value=str(frag_record.note_id))
        form.add_row("时间", "date_text", value=frag_record.date_text)
        form.add_textarea("内容", field="content", value=frag_record.content)
        
        kw = Storage()
        kw.form = form
        return self.response_form(**kw)
    
    def handle_save(self):
        param = self.get_param_dict()
        user_id = xauth.current_user_id()
        frag_id = param.get_int("frag_id")
        note_id = param.get_int("note_id")
        
        if frag_id > 0:
            frag_record = NoteFragmentDao.get_by_frag_id(frag_id=frag_id, user_id=user_id)
            if frag_record is None:
                return webutil.FailedResult(code="404", message="记录不存在")
        else:
            frag_record = NoteFragmentRecord()
            frag_record.user_id = user_id
            frag_record.note_id = note_id
            
        note_info = NoteIndexDao.get_by_id(note_id=note_id)
        if note_info is None:
            return webutil.FailedResult(code="404", message="笔记不存在")
        
        frag_record.content = param.get_str("content")
        frag_record.date_text = param.get_str("date_text")

        NoteFragmentDao.save(frag_record)
 
        return webutil.SuccessResult()

    def handle_delete(self):
        frag_id = xutils.get_argument_int("frag_id")
        user_id = xauth.current_user_id()
        NoteFragmentDao.delete_by_id(frag_id=frag_id, user_id=user_id)
        return webutil.SuccessResult()

xurls = (
    "/note/fragment", FragmentHandler,
)