import xutils

from xutils.base import Storage
from xutils import webutil
from xutils import textutil
from xnote.plugin.table_plugin import BaseTablePlugin, TableActionType
from xnote_handlers.config import LinkConfig
from xnote.open_api.dao import SystemSyncAppDao, SystemSyncAppRecord
from .system_sync_controller import get_system_sync_tab

class AppHandler(BaseTablePlugin):

    title = "应用管理"
    require_admin = True
    parent_link = LinkConfig.system_sync

    NAV_HTML = """
<div class="card">
    {% render system_sync_tab %}
</div>
"""
    
    def handle_page(self):
        table = self.create_table()
        table.add_head("app_id", field="app_id")
        table.add_head("app_name", field="app_name")
        table.add_head("app_key", field="app_key")
        table.add_head("remark", field="remark")
        table.add_action("编辑", link_field="edit_url", type=TableActionType.edit_form)
        table.add_action("删除", link_field="delete_url", type=TableActionType.confirm, 
                         msg_field="delete_msg", css_class="btn danger")

        records = SystemSyncAppDao.list()
        for record in records:
            record["edit_url"] = f"?action=edit&app_id={record.app_id}"
            record["delete_url"] = f"?action=delete&app_id={record.app_id}"
            record["delete_msg"] = f"确认删除[{record.app_name}]吗?"
            table.add_row(record)

        table.action_bar.add_edit_button("新增应用", url="?action=edit")

        kw = Storage()
        kw.system_sync_tab = get_system_sync_tab("app")
        kw.table = table
        kw.page = 1
        kw.page_total = len(records)
        kw.page_url = "?page="

        return self.response_page(**kw)
    
    def handle_edit(self):
        form = self.create_form()
        app_id = xutils.get_argument_int("app_id")

        record = SystemSyncAppDao.get_by_app_id(app_id)
        if record is None:
            record = SystemSyncAppRecord()

        form.add_row("app_id", "app_id", value=str(app_id), css_class="hide")
        form.add_row("app_name", "app_name", value=record.app_name)
        form.add_row("app_key", "app_key", value=record.app_key)
        if record.app_id > 0:
            form.add_row("app_secret", "app_secret", value=record.app_secret, readonly=True)
        form.add_textarea("备注信息", "remark", value=record.remark)
        
        kw = Storage()
        kw.form = form
        return self.response_form(**kw)
    
    def handle_save(self):
        param = self.get_param_dict()
        app_id = param.get_int("app_id")
        app_name = param.get_str("app_name")
        app_key = param.get_str("app_key")
        remark = param.get_str("remark")

        if app_name == "":
            return webutil.FailedResult(code="400", message="invalid app_name")
        
        if app_key == "":
            return webutil.FailedResult(code="400", message="invalid app_key")
        
        check_old = SystemSyncAppDao.get_by_app_key(app_key)
        if check_old != None and check_old.app_id != app_id:
            return webutil.FailedResult(code="400", message="app_key已经存在")
        
        record = SystemSyncAppRecord()
        record.app_id = app_id
        record.app_name = app_name
        record.app_key = app_key
        record.remark = remark
        record.app_secret = textutil.create_uuid()

        SystemSyncAppDao.save(record)
        return webutil.SuccessResult()
    
    def handle_delete(self):
        app_id = xutils.get_argument_int("app_id")
        SystemSyncAppDao.delete_by_id(app_id)
        return webutil.SuccessResult()


xurls = (
    r"/system/sync/app", AppHandler,
)