from xnote.core import xtables
from .message_model import MessageTemplateRecord

class MessageTemplateDao:

    db = xtables.get_table_by_name("msg_template")

    @classmethod
    def insert(cls, record: MessageTemplateRecord):
        return cls.db.insert(**record.to_save_dict())

    @classmethod
    def update(cls, record: MessageTemplateRecord):
        cls.db.update(where = dict(template_id = record.template_id), **record.to_save_dict())

    @classmethod
    def save(cls, record: MessageTemplateRecord):
        assert record.user_id > 0
        assert len(record.name) > 0

        if record.template_id == 0:
            return cls.insert(record)
        return cls.update(record)
    
    @classmethod
    def delete(cls, template_id = 0, user_id = 0):
        return cls.db.delete(where = dict(template_id = template_id, user_id = user_id))

    @classmethod
    def list_by_user(cls, user_id = 0, template_type=""):
        where_dict = dict(user_id=user_id)
        if template_type == "" or template_type == "all":
            pass
        else:
            where_dict["type"] = template_type # type: ignore
        result = cls.db.select(where = where_dict, order = "sort_num")
        return MessageTemplateRecord.from_dict_list(result)
    
    @classmethod
    def get_by_id(cls, template_id = 0, user_id = 0):
        result = cls.db.select_first(where = dict(template_id = template_id, user_id = user_id))
        return MessageTemplateRecord.from_dict(result)
    
    @classmethod
    def count(cls, user_id = 0):
        return cls.db.count(where=dict(user_id=user_id))
    

    
