import threading
from xnote.core import xtables
from xutils.base import BaseDataRecord
from xutils import dateutil
from xutils import interfaces

class IdGenerator(interfaces.IdGeneratorInterface):
    def __init__(self, biz_name: str):
        self.biz_name = biz_name
        self.lock = threading.RLock()
        self.segment = IdManager.next_segment(self.biz_name)
        self.current_id = self.segment.start_id

    def next_id(self):
        with self.lock:
            if self.current_id < self.segment.start_id:
                self.current_id = self.segment.start_id

            if self.current_id > self.segment.end_id:
                self.segment = IdManager.next_segment(self.biz_name)

            result_id = self.current_id
            self.current_id += 1
            return result_id


class IdGeneratorRecord(BaseDataRecord):
    def __init__(self):
        self.biz_name = ""
        self.version = 0
        self.current_max_id = 0
        self.step = 0
        self.range_start = 0
        self.range_end = 0
        self.create_time = 0
        self.update_time = 0

class Segment:
    def __init__(self, start_id = 0, end_id = 0):
        self.start_id = start_id
        self.end_id = end_id

class IdManager:

    db = xtables.get_table_by_name("id_generator")

    @classmethod
    def init_biz(cls, biz_name: str, current_max_id = 0, step = 10, range_start = 1, range_end = 0):
        record = cls.db.select_first(where = dict(biz_name=biz_name))
        if record != None:
            return
        
        now = dateutil.timestamp_ms()
        record = IdGeneratorRecord()
        record.biz_name = biz_name
        record.current_max_id = current_max_id
        record.step = step
        record.range_start = range_start
        record.range_end = range_end
        record.create_time = now
        record.update_time = now

        return cls.db.insert(**record.to_save_dict())
        

    @classmethod
    def next_segment(cls, biz_name: str, max_retry = 10):
        for retry in range(max_retry):
            first = cls.db.select_first(where = dict(biz_name=biz_name))
            assert first != None
            record = IdGeneratorRecord.from_dict(first)
            assert record.step > 0

            current_max_id = record.current_max_id
            start_id = current_max_id + 1
            if start_id < record.range_start:
                start_id = record.range_start

            next_max_id = start_id + record.step - 1
            update_time = dateutil.timestamp_ms()
            new_version = record.version + 1

            if record.range_end > 0 and next_max_id > record.range_end:
                raise Exception("next_max_id overflow")

            rows = cls.db.update(where = dict(biz_name = biz_name, version = record.version), 
                        current_max_id = next_max_id, update_time = update_time, version = new_version)
            
            if rows > 0:
                segment = Segment(start_id = start_id, end_id = next_max_id)
                return segment
        
        raise Exception("too many retries")
    

IdManager.init_biz("common", step=100)
default_generator = IdGenerator("common")