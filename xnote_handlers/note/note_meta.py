import xutils
from typing import List, Dict, Optional
from .models import NoteViewContext
from xnote.core import xconfig
from xnote.core import xauth
from xnote.plugin import TabBox, DataTable, TableActionType
from xnote.plugin.table_plugin import BaseTablePlugin
from xutils import webutil
from .models import NoteIndexDO
from .dao import NoteIndexDao
from .dao_meta import NoteMetaRecord, NoteMetaDao
from .note_meta_config import NoteMetaConfig, NoteMetaValueType, NoteMetaCategory

class NoteMetaService:
    
    @classmethod
    def render_note_view_ctx(cls, ctx: NoteViewContext):
        if ctx.tab != "meta":
            ctx.note_meta_list = cls.get_meta_list(note_id=ctx.note_id, note_info=ctx.file, view_tab="all")
            return
        
        ctx.hide_components()
        ctx.show_meta_manage = True
        
        tab = TabBox(tab_key="meta_category", tab_default="all")
        tab.add_item(title="全部", value="all")
        tab.add_item(title="基本信息", value="basic")
        tab.add_item(title="人物信息", value="people")
        tab.add_item(title="自定义", value="custom")
        
        meta_category = xutils.get_argument_str("meta_category", "all")        
        ctx.meta_tab = tab
        
        table = DataTable()
        table.add_head(title="属性名", field="meta_name")
        table.add_head(title="属性值", field="meta_value")
        table.add_action(title="编辑", type=TableActionType.edit_form, link_field="edit_url")
        table.add_action(
            title="清空", type=TableActionType.confirm, link_field="delete_url", 
            msg_field="delete_msg", css_class="btn danger")
        ctx.meta_table = table
        
        if meta_category == "all":
            cls._render_all(ctx, table)
            return

        return cls._render_category(ctx, table, meta_category)
    
    @classmethod
    def _render_category(cls, ctx: NoteViewContext, table:DataTable, meta_category: str):
        meta_list = cls.get_meta_list(note_id=ctx.note_id, note_info=ctx.file)
        meta_keys = set()
        
        for item in meta_list:
            cls._fill_links(item)
            is_custom = (meta_category == NoteMetaCategory.custom and item.meta_category == "")
            if item.meta_category == meta_category or is_custom:
                table.add_row(item)
                meta_keys.add(item.meta_key)
        
        for item in NoteMetaConfig.items():
            row = NoteMetaRecord()
            row.meta_name = item.meta_name
            row.meta_key = item.meta_key
            row.value_type = item.value_type
            row.note_id = ctx.note_id
            
            if meta_category == item.meta_category and row.meta_key not in meta_keys:
                cls._fill_links(row)
                table.add_row(row)
                
        
        
    @classmethod
    def _render_all(cls, ctx: NoteViewContext, table:DataTable):
        meta_list = cls.get_meta_list(note_id=ctx.note_id, note_info=ctx.file)
        
        meta_keys = set()
        
        for item in meta_list:
            cls._fill_links(item)
            table.add_row(item)
            meta_keys.add(item.meta_key)
        
        for item in NoteMetaConfig.items():
            row = NoteMetaRecord()
            row.meta_name = item.meta_name
            row.meta_key = item.meta_key
            row.value_type = item.value_type
            row.note_id = ctx.note_id
            
            if row.meta_key not in meta_keys:
                cls._fill_links(row)
                table.add_row(row)
                
    @classmethod
    def _fill_links(cls, row: NoteMetaRecord):
        assert row.note_id > 0
        q_meta_name = xutils.quote(row.meta_name)
        q_meta_value = ""
        if row.meta_id == 0:
            q_meta_value = xutils.quote(row.meta_value)
            
        row.edit_url = f"/note/meta?action=edit&meta_id={row.meta_id}&note_id={row.note_id}"\
            f"&value_type={row.value_type}&meta_key={row.meta_key}&meta_name={q_meta_name}&meta_value={q_meta_value}"
        
        if row.meta_id > 0:
            row.delete_url = f"/note/meta?action=delete&meta_id={row.meta_id}"
            row.delete_msg = f"确定清空属性【{row.meta_name}】吗"
        
    @classmethod
    def find_meta(cls, records:List[NoteMetaRecord], meta_key: str):
        for record in records:
            if record.meta_key == meta_key:
                return record
        return None
    
    @classmethod
    def get_meta_list(cls, note_id: int, note_info: Optional[NoteIndexDO] = None, view_tab = "meta"):
        records = NoteMetaDao.list_by_note_id(note_id=note_id)
        if note_info:
            records += note_info.to_meta_list(view_tab = view_tab)
            
        for record in records:
            meta_config = NoteMetaConfig.get_by_meta_key(record.meta_key)
            if meta_config:
                record.meta_name = meta_config.meta_name
                record.meta_category = meta_config.meta_category
            else:
                record.meta_name = record.meta_key
            
            cls._fill_links(record)
        return records

class NoteMetaHandler(BaseTablePlugin):
    
    require_admin = False
    require_login = True
    
    def handle_edit(self):
        meta_id = xutils.get_argument_int("meta_id")
        meta_key = xutils.get_argument_str("meta_key")
        meta_name = xutils.get_argument_str("meta_name")
        note_id = xutils.get_argument_int("note_id")
        user_id = xauth.current_user_id()
        
        meta_config = NoteMetaConfig.get_by_meta_key(meta_key)
        value_type = NoteMetaValueType.text
        if meta_config:
            value_type = meta_config.value_type
        
        if meta_id > 0:
            meta_info = NoteMetaDao.get_by_meta_id(meta_id=meta_id, user_id=user_id)
            if meta_info is None:
                return webutil.FailedResult(code="400", message="元信息不存在")
        else:
            meta_info = NoteMetaRecord()
            meta_info.meta_key = meta_key
            meta_info.note_id = note_id
            meta_info.meta_value = xutils.get_argument_str("meta_value")
            
        form = self.create_form()
        form.path = "/note/meta"
        form.add_row(title="note_id", field="note_id", value=str(meta_info.note_id), css_class="hide")
        form.add_row(title="meta_id", field="meta_id", value=str(meta_info.meta_id), css_class="hide")
        form.add_row(title="meta_key", field="meta_key", value=meta_info.meta_key, css_class="hide")
        
        readonly = True
        if meta_key == "_new_custom":
            readonly = False
            meta_name = ""
            
        form.add_row(title="属性名", field="meta_name", value=meta_name, readonly=readonly)
        
        if value_type == NoteMetaValueType.date:
            form.add_date_input(title="属性值", field="meta_value", value=meta_info.meta_value)
        elif value_type == NoteMetaValueType.number:
            form.add_row(title="属性值", field="meta_value", value=meta_info.meta_value)
        else:
            form.add_textarea(title="属性值", field="meta_value", value=meta_info.meta_value)
        
        return self.response_form(form=form)
    
    def handle_save(self):
        user_id = xauth.current_user_id()
        data = self.get_param_dict()
        meta_id = data.get_int("meta_id")
        meta_key = data.get_str("meta_key")
        meta_name = data.get_str("meta_name")
        note_id = data.get_int("note_id")
        
        if note_id <= 0:
            return webutil.FailedResult(code="400", message="invalid note_id")
        
        if meta_id > 0:
            meta_info = NoteMetaDao.get_by_meta_id(meta_id=meta_id, user_id=user_id)
            if meta_info is None:
                return webutil.FailedResult(code="400", message="元信息不存在")
        else:
            meta_info = NoteMetaRecord()
        
        if meta_key == "_new_custom":
            meta_key = meta_name
            if meta_name == "":
                return webutil.FailedResult(code="400", message="属性名为空")
            
        old = NoteMetaDao.get_by_meta_key(note_id=note_id, meta_key=meta_key)
        if old != None and old.meta_id != meta_id:
            return webutil.FailedResult(code="400", message=f"属性[{meta_name}]已经存在")
            
        meta_info.user_id = user_id
        meta_info.meta_key = meta_key
        meta_info.meta_value = data.get_str("meta_value")
        meta_info.note_id = note_id
        
        meta_config = NoteMetaConfig.get_by_meta_key(meta_key)
        if meta_config and meta_config.is_note_field:
            try:
                NoteIndexDao.update_field(meta_info)
            except Exception as e:
                return webutil.FailedResult(message=str(e))
            return webutil.SuccessResult()
            
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