# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2024-04-04 00:01:38
@LastEditors  : xupingmao
@LastEditTime : 2024-07-06 16:20:57
@FilePath     : /xnote/tests/test_service.py
@Description  : 描述
"""
import time
import threading

from . import test_base
from xnote.core import xtables
from xnote.service import DatabaseLockService
from xnote.service import TagBindServiceImpl
from xnote.service import TagTypeEnum
from xnote.service.id_service import IdGenerator, IdGeneratorRecord, IdService

app = test_base.init()

class TestMain(test_base.BaseTestCase):
    """测试管理后台的功能"""

    db = xtables.get_table_by_name("t_lock")

    def get_lock_record_by_key(self, lock_key=""):
        return self.db.select_first(where=dict(lock_key=lock_key))    
    
    def test_lock_service_conflict(self):
        lock_key = "test_conflict"

        lock1 = DatabaseLockService.lock(lock_key)
        assert self.get_lock_record_by_key(lock_key) != None

        try:
            lock2 = DatabaseLockService.lock(lock_key)
            assert False
        except:
            assert True
        
        lock1.release()

        assert self.get_lock_record_by_key(lock_key) == None
    
    def test_lock_and_free(self):
        lock_key = "test_lock_and_free"
        with DatabaseLockService.lock(lock_key):
            assert self.get_lock_record_by_key(lock_key) != None
            print("do some work")
        
        assert self.get_lock_record_by_key(lock_key) == None

    def test_lock_timeout(self):
        lock_key = "test_lock_timeout"
        with DatabaseLockService.lock(lock_key, timeout_seconds=0.1):
            assert self.get_lock_record_by_key(lock_key) != None
            time.sleep(0.5)
            t2 = DatabaseLockService.lock(lock_key)
            assert t2.got_lock
            current_lock = self.get_lock_record_by_key(lock_key)
            assert current_lock != None
            assert current_lock.lock_token == t2.lock_token
        
        current_lock = self.get_lock_record_by_key(lock_key)
        assert current_lock != None


    def test_tag_service(self):
        service = TagBindServiceImpl(tag_type=TagTypeEnum.msg_tag.int_value)
        user_id = 1
        target_id = 1234
        # delete all tag binds
        service.bind_tags(user_id=user_id, target_id=target_id, tags=[])
        count = service.count_user_tag(user_id=user_id, target_id=target_id)
        assert count == 0

        service.bind_tags(user_id=user_id, target_id=target_id, tags=["tag1", "tag2"])
        count = service.count_user_tag(user_id=user_id, target_id=target_id)
        assert count == 2
        bindlist = service.get_by_target_id(user_id=user_id, target_id=target_id)
        bindlist.sort(key = lambda x:x.tag_code)
        assert len(bindlist) == 2
        assert bindlist[0].tag_code == "tag1"
        assert bindlist[1].tag_code == "tag2"

    def test_tag_service_with_second_type(self):
        service = TagBindServiceImpl(tag_type=TagTypeEnum.msg_tag.int_value)
        user_id = 1
        target_id = 1234
        type1 = 1

        # delete all tag binds
        service.bind_tags(user_id=user_id, target_id=target_id, tags=[])
        count = service.count_user_tag(user_id=user_id, target_id=target_id)
        assert count == 0

        service.bind_tags(user_id=user_id, target_id=target_id, tags=["tag1", "tag2"], second_type=type1)
        count = service.count_user_tag(user_id=user_id, target_id=target_id, second_type=type1)
        assert count == 2
        bindlist = service.get_by_target_id(user_id=user_id, target_id=target_id, second_type=type1)
        bindlist.sort(key = lambda x:x.tag_code)
        assert len(bindlist) == 2
        assert bindlist[0].tag_code == "tag1"
        assert bindlist[0].second_type == type1
        assert bindlist[1].tag_code == "tag2"
        assert bindlist[1].second_type == type1

    def run_id_test(self, biz_name="test", step = 1):
        IdService.init_biz(biz_name, current_max_id=0, range_start=1, step=step)
        id_gen = IdGenerator(biz_name)

        assert id_gen.next_id() == 1
        assert id_gen.next_id() == 2

        def gen_id_func():
            id_gen.next_id()

        plist = [threading.Thread(target=gen_id_func) for x in range(10)]
        for p in plist:
            p.start()

        for p in plist:
            p.join()

        assert id_gen.next_id() == 2 + 10 + 1

    def test_id_service(self):
        self.run_id_test(biz_name="test1", step = 1)
        self.run_id_test(biz_name="test5", step = 5)


