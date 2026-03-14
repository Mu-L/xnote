from xutils.base import BaseEnum, EnumItem, BaseDataRecord
from xnote.core import xtables
from xutils import quote
from xutils import dateutil


class TagInfoDO(BaseDataRecord):
    def __init__(self, **kw):
        self.tag_id = 0
        self.ctime = xtables.DEFAULT_DATETIME
        self.mtime = xtables.DEFAULT_DATETIME
        self.user_id = 0
        self.tag_type = 0
        self.second_type = 0
        self.tag_code = ""
        self.tag_name = ""
        self.score = 0.0
        self.amount = 0
        self.visit_cnt = 0
        self.category_id = 0
        self.update(kw)

    def handle_from_dict(self):
        if self.tag_name == "":
            self.tag_name = SystemTagEnum.get_name_by_code(self.tag_code)

    def to_save_dict(self):
        result = dict(**self)
        result.pop("tag_id", None)
        result.pop("tag_name", None)
        return result
    
    @property
    def url(self):
        if self.tag_type == TagTypeEnum.msg_tag.int_value:
            if SystemTagEnum.is_sys_tag(self.tag_code):
                return f"/message/system_tag?tag_code={self.tag_code}"
            return f"/message?tag=search&key={quote(self.tag_code)}"
        return f"/note/taginfo?tag_code={quote(self.tag_code)}"
    
    @property
    def tag_type_name(self):
        return TagTypeEnum.get_name_by_value(str(self.tag_type))
        

class TagBindRecord(BaseDataRecord):
    """标签绑定信息, 业务唯一键=tag_type+tag_code+target_id"""
    
    _ignore_save_fields = ["id"]
    
    def __init__(self):
        self.ctime = dateutil.format_datetime()
        self.user_id = 0
        self.tag_type = 0
        self.tag_code = ""
        self.target_id = 0    # target_id 对应的是 tag_type
        self.second_type = 0  # 二级类型, 这是target_id实体的一个属性
        self.sort_value = ""  # 排序字段

    @property
    def tag_name(self):
        return SystemTagEnum.get_name_by_code(self.tag_code)
    
    @property
    def is_note_type(self):
        return self.tag_type == TagTypeEnum.note_tag.int_value

TagBind = TagBindRecord

class SystemTagEnum(BaseEnum):
    todo = EnumItem("待办", "_todo")
    important = EnumItem("重要", "_important")
    file = EnumItem("文件", "_file")
    link = EnumItem("链接", "_link")
    book = EnumItem("书籍", "_book")
    people = EnumItem("人物", "_people")
    phone = EnumItem("电话", "_phone")

    _enums = [todo, important, file, link, book, people, phone]
    _note_enums = [todo, important]

    @staticmethod
    def is_sys_tag(tag_code=""):
        return SystemTagEnum.get_by_value(tag_code) != None
    
    @classmethod
    def get_name_by_code(cls, tag_code=""):        
        for item in cls._enums:
            if item.value == tag_code:
                return item.name
        return tag_code

    @classmethod
    def get_note_tags(cls):
        result = [] # type: list[TagInfoDO]
        for item in cls._note_enums:
            result.append(TagInfoDO(tag_code=item.value, tag_name=item.name))
        return result

class TagTypeEnum(BaseEnum):
    """标准库的枚举无法扩展,所以这里不用,从外部添加枚举值可以直接设置新的属性"""
    note_tag = EnumItem("笔记标签", "1")
    msg_tag = EnumItem("随手记标签", "2")


class TagPrefixEnum:
    heading = EnumItem("标题标签", "_h:")


