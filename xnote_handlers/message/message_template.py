import xutils
from xnote.core import xauth
from xnote.plugin.table_plugin import BaseTablePlugin, TableActionType
from xutils import dateutil, Storage
from xutils import webutil, textutil
from .dao_template import MessageTemplateDao, MessageTemplateRecord
from xnote_handlers.config import LinkConfig

class TemplateHandler(BaseTablePlugin):

    require_login = True
    title = "模板"
    parent_link = LinkConfig.message

    def handle_page(self):
        user_id = xauth.current_user_id()
        datalist = MessageTemplateDao.list_by_user(user_id=user_id)

        table = self.create_table()
        table.action_bar.add_edit_button(text="新增模板", url="?action=edit")
        table.default_head_style.min_width = "100px"
        table.add_head("模板ID", "template_id")
        table.add_head("模板顺序", "sort_num")
        table.add_head("模板名称", "name")
        table.add_head("更新日期", "update_date")
        table.add_head("模板内容", "content_short")

        table.add_action("编辑", link_field="edit_url", type=TableActionType.edit_form)
        table.add_action("删除", link_field="delete_url", type=TableActionType.confirm, msg_field="delete_msg", css_class="btn danger")

        for data in datalist:
            data["update_date"] = dateutil.format_date(data.mtime)
            data["edit_url"] = f"?action=edit&template_id={data.template_id}"
            data["delete_url"] = f"?action=delete&template_id={data.template_id}"
            data["delete_msg"] = f"确认删除模板【{data.name}】吗?"
            data["content_short"] = textutil.get_short_text(data.content, 50)
            table.add_row(data)
        
        kw = Storage()
        kw.table = table
        return self.response_page(**kw)
    
    def handle_edit(self):
        user_id = xauth.current_user_id()
        template_id = xutils.get_argument_int("template_id")

        if template_id > 0:
            record = MessageTemplateDao.get_by_id(template_id=template_id, user_id=user_id)
            if record is None:
                return self.response_text("无效的数据")
        else:
            record = MessageTemplateRecord()
            record.sort_num = MessageTemplateDao.count(user_id=user_id) * 10
        
        form = self.create_form()
        form.add_row("template_id", "template_id", value=str(template_id), css_class="hide")        
        form.add_row("模板名称", "name", value=record.name)
        form.add_textarea("模板内容", "content", value=record.content)
        form.add_row("模板排序", "sort_num", value=str(record.sort_num))
        
        kw = Storage()
        kw.form = form
        return self.response_form(**kw)
    
    def handle_save(self):
        user_id = xauth.current_user_id()
        param = self.get_param_dict()
        template_id = param.get_int("template_id")
        if template_id == 0:
            record = MessageTemplateRecord()
            record.user_id = user_id
        else:
            record = MessageTemplateDao.get_by_id(template_id=template_id, user_id=user_id)

        record.name = param.get_str("name")
        record.content = param.get_str("content")
        record.mtime = dateutil.format_datetime()
        record.sort_num = param.get_int("sort_num")

        if record.name == "":
            return webutil.FailedResult(message="模板名称不能为空")

        MessageTemplateDao.save(record)
        return webutil.SuccessResult()
    
    def handle_delete(self):
        user_id = xauth.current_user_id()
        template_id = xutils.get_argument_int("template_id")
        MessageTemplateDao.delete(template_id=template_id, user_id=user_id)
        return webutil.SuccessResult()
    

xurls = (
    "/message/template", TemplateHandler,
)