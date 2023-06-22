# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2020/01/24 16:39:45
# @modified 2022/04/04 14:11:51

import sys
import time
import unittest
sys.path.insert(1, "lib")
sys.path.insert(1, "core")
import xauth
from xutils import Storage
from xutils import dateutil

# cannot perform relative import
try:
    import test_base
except ImportError:
    from tests import test_base

BaseTestCase = test_base.BaseTestCase

app = test_base.init()

class TestXauth(BaseTestCase):

    def test_current_user(self):
        self.assertEqual("test", xauth.current_name())

    def test_check_invalid_names(self):
        self.assertTrue(xauth.is_valid_username("t1234"))
        self.assertFalse(xauth.is_valid_username("public"))

    def test_create_and_delete_user(self):
        old_count = xauth.count_user()

        # 创建用户
        result = xauth.create_user("u123456", "123456")
        print(result)
        
        self.assertEqual(old_count+1, xauth.count_user())

        # 删除用户
        xauth.delete_user("u123456")

        check = xauth.find_by_name("u123456")
        self.assertEqual(None, check)

    def test_count_user(self):
        self.assertTrue(xauth.count_user() >= 1)

    def test_login_logout(self):
        self.check_OK("/")
        # TODO 待修复
        # AttributeError: 'ThreadedDict' object has no attribute 'homepath'
        # xauth.login_user_by_name("test")
        # xauth.logout_current_user()

    def test_create_and_list_user_session(self):
        # 先清理
        for session_info in xauth.list_user_session_detail("admin"):
            xauth.delete_user_session_by_id(session_info.sid)

        # 创建并且查询
        xauth.create_user_session("admin")
        result = xauth.list_user_session_detail("admin")
        self.assertEqual(1, len(result))

    def test_update_user(self):
        result = xauth.create_user("u123456", "123456")
        print(result)

        datetime = dateutil.format_time()
        user_info = Storage(login_time = datetime)
        xauth.update_user("u123456", user_info)

        self.assertTrue(datetime, xauth.get_user_by_name("u123456").login_time)

        xauth.delete_user("u123456")

    def test_get_user_by_token(self):
        user_name = "u123456"
        result = xauth.create_user(user_name, "123456")
        print(result)

        datetime = dateutil.format_time()
        token = "token123456"
        user_info = Storage(login_time = datetime)
        user_info.token = token

        xauth.update_user("u123456", user_info)

        found = xauth.UserModel.get_by_token(token)
        self.assertEqual(user_name, found.name)

        xauth.delete_user("u123456")

    def test_user_config(self):
        user_name = "u123456"
        result = xauth.create_user(user_name, user_name)
        print(result)

        config = xauth.get_user_config_dict(user_name)
        self.assertEqual("false", config.show_comment_edit)

        xauth.update_user_config(user_name, "show_comment_edit", "true")

        config = xauth.get_user_config_dict(user_name)
        self.assertEqual("true", config.show_comment_edit)

        xauth.delete_user(user_name)


    def test_create_quick_user(self):
        user_info = xauth.create_quick_user()
        assert user_info != None
        assert len(user_info.password_md5) > 0
        xauth.delete_user(user_info.name)


    def test_change_password(self):
        user_name = "change_pass_test"
        password = "123456"
        xauth.delete_user(user_name)
        resp = xauth.create_user(user_name, password)
        assert resp.get("code") == "success"
        xauth.check_old_password(user_name, password)
        try:
            xauth.check_old_password(user_name, password + "2")
            self.fail("expect exception")
        except:
            pass