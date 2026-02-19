from typing import Optional, List
from xutils.base import BaseDataRecord
from xnote.core import xtables
from xutils import dateutil
from .models import NoteMetaRecord

class NoteMetaDao:
    
    db = xtables.get_table_by_name("note_meta")
    
    @classmethod
    def save(cls, record: NoteMetaRecord):
        record.update_time = dateutil.timestamp_ms()
        record.validate()
        if record.meta_id > 0:
            cls.db.update(where = dict(meta_id = record.meta_id), **record.to_save_dict())
        else:
            new_id = cls.db.insert(**record.to_save_dict())
            record.meta_id = int(new_id)

    @classmethod
    def list_by_note_id(cls, note_id=0, meta_keys: Optional[list] = None) -> List[NoteMetaRecord]:
        where_sql = "note_id = $note_id"
        if meta_keys != None:
            if len(meta_keys) == 0:
                return []
            where_sql += " AND meta_key in $meta_keys"
        vars = dict(note_id=note_id, meta_keys=meta_keys)
        results = cls.db.select(where=where_sql, vars = vars)
        return NoteMetaRecord.from_dict_list(results)

    @classmethod
    def get_by_meta_id(cls, meta_id=0, user_id=0):
        result = cls.db.select_first(where = dict(meta_id=meta_id, user_id=user_id))
        return NoteMetaRecord.from_dict_or_None(result)
    
    @classmethod
    def delete_by_meta_id(cls, meta_id=0, user_id=0):
        return cls.db.delete(where = dict(meta_id=meta_id, user_id=user_id))
    
    @classmethod
    def delete_by_note_id(cls, note_id=0):
        return cls.db.delete(where = dict(note_id = note_id))

