from xutils.base import BaseDataRecord
from xutils import dateutil
from xnote.core import xtables

class SystemSyncAppRecord(BaseDataRecord):
    _ignore_save_fields = set(["app_id"])

    def __init__(self):
        self.app_id = 0
        self.create_time = dateutil.timestamp_ms()
        self.update_time = dateutil.timestamp_ms()
        self.version = 0
        self.app_name = ""
        self.app_key = ""
        self.app_secret = "" # TODO 后面考虑加密
        self.remark = ""



class SystemSyncAppDao:

    db = xtables.get_table_by_name("system_sync_app")

    @classmethod
    def get_by_app_key(cls, app_key: str):
        result = cls.db.select_first(where = dict(app_key=app_key))
        return SystemSyncAppRecord.from_dict_or_None(result)

    @classmethod
    def get_by_app_id(cls, app_id: int):
        result = cls.db.select_first(where = dict(app_id=app_id))
        return SystemSyncAppRecord.from_dict_or_None(result)

    @classmethod
    def list(cls, offset=0, limit = 20):
        results = cls.db.select(offset=offset, limit=limit)
        return SystemSyncAppRecord.from_dict_list(results)
    
    @classmethod
    def save(cls, record: SystemSyncAppRecord):
        if record.app_id == 0:
            cls.db.insert(**record.to_save_dict())
        else:
            old_version = record.version
            record.update_time = dateutil.timestamp_ms()
            record.version += 1
            rows = cls.db.update(where = dict(app_id = record.app_id, version = old_version), **record.to_save_dict())
            assert rows > 0

    @classmethod
    def delete_by_id(cls, app_id: int):
        return cls.db.delete(where = dict(app_id = app_id))


 
