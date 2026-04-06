from typing import List, Dict, Optional

class NoteMetaValueType:
    text = "text"
    date = "date"
    select = "select"
    number = "number"
    
class NoteMetaCategory:
    basic = "basic"
    people = "people"
    custom = "custom"

class NoteMetaItem:
    def __init__(self, meta_name="", meta_key="", meta_category="", value_type="", is_note_field=False):
        self.meta_key = meta_key
        self.meta_name = meta_name
        self.meta_category = meta_category
        self.value_type = value_type
        self.is_note_field = is_note_field

class NoteMetaDateItem(NoteMetaItem):
    def __init__(self, meta_name="", meta_key="", meta_category=""):
        super().__init__(meta_name, meta_key, meta_category, NoteMetaValueType.date)

class NoteMetaNumberItem(NoteMetaItem):
    def __init__(self, meta_name="", meta_key="", meta_category=""):
        super().__init__(meta_name, meta_key, meta_category, NoteMetaValueType.number)
    
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
    def add_item(cls, meta_item: NoteMetaItem):
        """添加配置项, 插件可以通过这个接口新增配置项"""
        old = cls.get_by_meta_key(meta_item.meta_key)
        if old is not None:
            return
        cls._items.append(meta_item)
        cls._dict[meta_item.meta_key] = meta_item

    @classmethod
    def add_items(cls, items: List[NoteMetaItem], meta_category = ""):
        for item in items:
            if meta_category != "":
                item.meta_category = meta_category
            cls.add_item(item)
            
NoteMetaConfig.add_items([
    NoteMetaItem(meta_name="笔记类型", meta_key="_type", value_type=NoteMetaValueType.select, is_note_field=True),
    NoteMetaItem(meta_name="创建日期", meta_key="_create_date", value_type=NoteMetaValueType.date, is_note_field=True),
    NoteMetaItem(meta_name="人工简介", meta_key="_manual_short_desc", value_type=NoteMetaValueType.text, is_note_field=True),
], meta_category=NoteMetaCategory.basic)

NoteMetaConfig.add_items([
    NoteMetaNumberItem(meta_name="出生年份", meta_key="birth_year"),
    NoteMetaDateItem(meta_name="出生日期", meta_key="birth_date"),
    NoteMetaItem(meta_name="手机号", meta_key="mobile"),
    NoteMetaItem(meta_name="公司", meta_key="company"),
    NoteMetaItem(meta_name="地址", meta_key="address"),
], meta_category=NoteMetaCategory.people)

NoteMetaConfig.add_items([
    NoteMetaItem(meta_name="新增自定义属性", meta_key="_new_custom"),
], meta_category=NoteMetaCategory.custom)
