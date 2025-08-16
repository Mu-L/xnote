from xnote.core import xtables
from xutils import BaseDataRecord
from xutils import DEFAULT_DATETIME
from xutils import dateutil
from web.db import SQLLiteral

class SystemInfoRecord(BaseDataRecord):
    def __init__(self, **kw):
        self.id = 0
        self.ctime = DEFAULT_DATETIME
        self.mtime = DEFAULT_DATETIME
        self.info_key = ""
        self.info_value = ""
        self.version = 0
        self.update(kw)

    def to_save_dict(self):
        result = dict(**self)
        result.pop("id", None)
        return result

class SystemInfoService:

    db = xtables.get_table("system_info")

    @classmethod
    def set_info(cls, info_key: str, info_value: str):
        rowcount = int(cls.db.update(where=dict(info_key=info_key), info_value=info_value, version = SQLLiteral("version+1")))
        if rowcount > 0:
            return
        record = SystemInfoRecord()
        record.info_key = info_key
        record.info_value = info_value
        record.ctime = dateutil.format_datetime()
        record.mtime = dateutil.format_datetime()
        cls.db.insert(**record.to_save_dict())

    @classmethod
    def get_info(cls, info_key: str):
        record = cls.db.select_first(where = dict(info_key = info_key))
        return SystemInfoRecord.from_dict_or_None(record)

    @classmethod
    def get_info_value(cls, info_key: str):
        info = cls.get_info(info_key)
        if info:
            return info.info_value
        return None
