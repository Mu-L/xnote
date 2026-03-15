
from xnote.core import xtables
from .models import NoteFragmentRecord
from xutils import dateutil

class NoteFragmentDao:
    
    db = xtables.get_table_by_name("note_fragment")
    
    @classmethod
    def list_by_note_id(cls, note_id: int, limit=1000):
        results = cls.db.select(where=dict(note_id=note_id), limit=limit, order="date_text desc")
        return NoteFragmentRecord.from_dict_list(results)
    

    @classmethod
    def get_by_frag_id(cls, frag_id: int, user_id: int):
        record = cls.db.select_first(where=dict(frag_id=frag_id, user_id=user_id))
        return NoteFragmentRecord.from_dict(record)

    @classmethod
    def save(cls, record: NoteFragmentRecord):
        record.update_time = dateutil.timestamp_ms()
        
        if record.frag_id > 0:
            return cls.db.update(where=dict(frag_id=record.frag_id), **record.to_save_dict())
        else:
            assert len(record.frag_type) > 0, "invalid frag_type"
            record.create_time = dateutil.timestamp_ms()
            return cls.db.insert(**record.to_save_dict())
        
    @classmethod
    def delete_by_id(cls, frag_id: int, user_id: int):
        return cls.db.delete(where=dict(frag_id=frag_id, user_id=user_id))