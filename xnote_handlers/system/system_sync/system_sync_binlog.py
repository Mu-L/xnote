import xutils

from xutils.base import Storage
from xutils import webutil
from xutils import dateutil
from xnote.plugin.table_plugin import BaseTablePlugin, TableActionType
from xnote_handlers.config import LinkConfig
from xutils.db.binlog import BinLogRecord, BinLog
from .system_sync_controller import get_system_sync_tab

class BinlogHandler(BaseTablePlugin):

    title = "binlog"
    require_admin = True
    parent_link = LinkConfig.app_index

    NAV_HTML = """
<div class="card">
    {% render system_sync_tab %}
</div>
"""
    
    def handle_page(self):
        page = xutils.get_argument_int("page")
        page_size = 20
        offset = (page-1) * page_size

        table = self.create_table()
        table.add_head("binlog_id", field="binlog_id")
        table.add_head("table_name", field="table_name")
        table.add_head("record_key", field="record_key")
        table.add_head("record_value", field="record_value")
        table.add_head("create_time", field="create_time_str")

        binlog = BinLog.get_instance()

        records = binlog.raw_list(offset=offset, limit=page_size, order="binlog_id desc")
        total = binlog.count_size()
        for record in records:
            record["create_time_str"] = dateutil.format_datetime(record.create_time, is_ms=True)
            table.add_row(record)

        kw = Storage()
        kw.system_sync_tab = get_system_sync_tab("binlog")
        kw.table = table
        kw.page = page
        kw.page_total = total
        kw.page_url = "?page="

        return self.response_page(**kw)

xurls = (
    r"/system/sync/binlog", BinlogHandler,
)