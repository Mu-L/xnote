import xutils
from typing import List, Dict
from .models import NoteViewContext
from xnote.core import xconfig
from xnote.core import xauth
from xnote.plugin import TabBox, DataTable, TableActionType
from xnote.plugin.table_plugin import BaseTablePlugin
from xutils import webutil
from .dao_meta import NoteMetaRecord, NoteMetaDao

class NoteMetaValueType:
    date = "date"

class NoteMetaItem:
    def __init__(self, meta_name="", meta_key="", meta_category="", value_type=""):
        self.meta_key = meta_key
        self.meta_name = meta_name
        self.meta_category = meta_category
        self.value_type = value_type

class NoteMetaDateItem(NoteMetaItem):
    def __init__(self, meta_name="", meta_key="", meta_category=""):
        super().__init__(meta_name, meta_key, meta_category, NoteMetaValueType.date)
    
class NoteMetaConfig:
    
    _items: List[NoteMetaItem] = []
    _dict: Dict[str, NoteMetaItem] = {}
    
    @classmethod
    def items(cls):
        return cls._items
    
    @classmethod
    def get_by_meta_key(cls, meta_key: str):
        return cls._dict.get(meta_key)
    
    @classmethod
    def get_name_by_key(cls, meta_key: str):
        info = cls._dict.get(meta_key)
        if info:
            return info.meta_name
        return meta_key
    
    @classmethod
    def add_item(cls, enum_item: NoteMetaItem):
        """添加配置项, 插件可以通过这个接口新增配置项"""
        old = cls.get_by_meta_key(enum_item.meta_key)
        if old is not None:
            return
        cls._items.append(enum_item)
        cls._dict[enum_item.meta_key] = enum_item

    @classmethod
    def add_items(cls, items: List[NoteMetaItem]):
        for item in items:
            cls.add_item(item)

NoteMetaConfig.add_items([
    NoteMetaDateItem(meta_name="出生日期", meta_key="birthday", meta_category="people"),
    NoteMetaItem(meta_name="公司", meta_key="company", meta_category="people"),
])

class NoteMetaService:
    
    @classmethod
    def render_note_view_ctx(cls, ctx: NoteViewContext):
        if ctx.tab != "meta":
            ctx.note_meta_list = cls.get_meta_list(note_id=ctx.note_id)
            return
        
        ctx.hide_components()
        ctx.show_meta_manage = True
        
        tab = TabBox(tab_key="meta_category", tab_default="all")
        tab.add_item(title="全部", value="all")
        tab.add_item(title="人物信息", value="people")
        tab.add_item(title="提醒信息", value="remind")
        
        meta_category = xutils.get_argument_str("meta_category", "all")
        note_id = ctx.note_id
        
        ctx.meta_tab = tab
        
        table = DataTable()
        table.add_head(title="属性名", field="meta_name")
        table.add_head(title="属性值", field="meta_value")
        table.add_action(title="编辑", type=TableActionType.edit_form, link_field="edit_url")
        table.add_action(
            title="清空", type=TableActionType.confirm, link_field="delete_url", 
            msg_field="delete_msg", css_class="btn danger")
        
        meta_keys = []
        meta_rows: List[NoteMetaRecord] = []
        for item in NoteMetaConfig.items():
            row = NoteMetaRecord()
            row.meta_name = item.meta_name
            row.meta_key = item.meta_key
            row.value_type = item.value_type
            row.note_id = note_id
            
            if meta_category == "all" or meta_category == item.meta_category:
                meta_rows.append(row)
                meta_keys.append(item.meta_key)
                table.add_row(row)
        
        records = NoteMetaDao.list_by_note_id(note_id=ctx.note_id, meta_keys = meta_keys)
        cls.fill_record_values(meta_rows, records)
        ctx.meta_table = table
        
    @classmethod
    def fill_record_values(cls, meta_rows: List[NoteMetaRecord], records: List[NoteMetaRecord]):
        for row in meta_rows:
            meta_info = cls.find_meta(records, row.meta_key)
            if meta_info:
                row.meta_id = meta_info.meta_id
                row.meta_value = meta_info.meta_value
            q_meta_name = xutils.quote(row.meta_name)
            row.edit_url = f"/note/meta?action=edit&meta_id={row.meta_id}&note_id={row.note_id}"\
                f"&value_type={row.value_type}&meta_key={row.meta_key}&meta_name={q_meta_name}"
            row.delete_url = f"/note/meta?action=delete&meta_id={row.meta_id}"
            row.delete_msg = f"确定清空属性【{row.meta_name}】吗"
        
    @classmethod
    def find_meta(cls, records:List[NoteMetaRecord], meta_key: str):
        for record in records:
            if record.meta_key == meta_key:
                return record
        return None
    
    @classmethod
    def get_meta_list(cls, note_id: int):
        records = NoteMetaDao.list_by_note_id(note_id=note_id)
        for record in records:
            record.meta_name = NoteMetaConfig.get_name_by_key(record.meta_key)
        return records

class NoteMetaHandler(BaseTablePlugin):
    
    require_admin = False
    require_login = True
    
    def handle_edit(self):
        meta_id = xutils.get_argument_int("meta_id")
        meta_key = xutils.get_argument_str("meta_key")
        meta_name = xutils.get_argument_str("meta_name")
        note_id = xutils.get_argument_int("note_id")
        value_type = xutils.get_argument_str("value_type")
        user_id = xauth.current_user_id()
        
        if meta_id > 0:
            meta_info = NoteMetaDao.get_by_meta_id(meta_id=meta_id, user_id=user_id)
            if meta_info is None:
                return webutil.FailedResult(code="400", message="元信息不存在")
        else:
            meta_info = NoteMetaRecord()
            meta_info.meta_key = meta_key
            meta_info.note_id = note_id
            
        form = self.create_form()
        form.path = "/note/meta"
        form.add_row(title="note_id", field="note_id", value=str(meta_info.note_id), css_class="hide")
        form.add_row(title="meta_id", field="meta_id", value=str(meta_info.meta_id), css_class="hide")
        form.add_row(title="meta_key", field="meta_key", value=meta_info.meta_key, css_class="hide")
        form.add_row(title="属性名", field="meta_name", value=meta_name, readonly=True)
        
        if value_type == NoteMetaValueType.date:
            form.add_date_input(title="属性值", field="meta_value", value=meta_info.meta_value)
        else:
            form.add_textarea(title="属性值", field="meta_value", value=meta_info.meta_value)
        
        return self.response_form(form=form)
    
    def handle_save(self):
        user_id = xauth.current_user_id()
        data = self.get_param_dict()
        meta_id = data.get_int("meta_id")
        
        if meta_id > 0:
            meta_info = NoteMetaDao.get_by_meta_id(meta_id=meta_id, user_id=user_id)
            if meta_info is None:
                return webutil.FailedResult(code="400", message="元信息不存在")
        else:
            meta_info = NoteMetaRecord()
        
        meta_info.user_id = user_id
        meta_info.meta_key = data.get_str("meta_key")
        meta_info.meta_value = data.get_str("meta_value")
        meta_info.note_id = data.get_int("note_id")
        NoteMetaDao.save(meta_info)
        return webutil.SuccessResult()
    
    def handle_delete(self):
        meta_id = xutils.get_argument_int("meta_id")
        user_id = xauth.current_user_id()
        meta_info = NoteMetaDao.get_by_meta_id(meta_id=meta_id, user_id=user_id)
        if meta_info is None:
            return webutil.FailedResult(code="400", message="元信息不存在")
        NoteMetaDao.delete_by_meta_id(meta_id=meta_id, user_id=user_id)
        return webutil.SuccessResult()
    

xurls = (
    "/note/meta", NoteMetaHandler,
)