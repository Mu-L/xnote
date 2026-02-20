# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2020/11/29 14:45:21
# @modified 2022/06/03 14:33:36
import xutils
from .a import *
import os
from xnote.core import xconfig
from xnote.core import xauth
from xutils import textutil, jsonutil, fsutil
from zipfile import ZipFile
from .test_base import json_request, BaseTestCase, request_html, json_request_return_dict
from .test_base import init as init_app, get_test_file_path
from xnote_handlers.fs.fs_index import build_fs_index
from xnote_handlers.fs.fs_helper import FileInfoDao, FileInfo

init_app()


class TestMain(BaseTestCase):

    def prepare_test_file(self, fname="", content=""):
        fpath = get_test_file_path(fname)
        with open(fpath, "w+") as fp:
            fp.write(content)
        return fpath

    def test_fs_view_mode(self):
        cwd = os.getcwd()

        self.check_OK(f"/fs/~{cwd}")
        self.check_OK(f"/fs/~{cwd}?mode=grid")
        self.check_OK(f"/fs/~{cwd}?mode=sidebar")

    def test_fs_hex(self):
        self.check_OK("/fs_hex")
        self.check_OK("/fs_hex?path=./README.md")

    def test_code_edit(self):
        self.check_OK("/code/edit?path=./README.md")
    
    def test_code_edit_part(self):
        old_config = xconfig.MAX_TEXT_SIZE
        xconfig.MAX_TEXT_SIZE = 100
        self.check_OK("/code/edit?path=./README.md")
        xconfig.MAX_TEXT_SIZE = old_config

    def test_code_edit_config(self):
        self.check_OK("/code/edit/config?config_key=config.init.script")
        data = dict(config_key = "config.init.script", content = "# init script")
        result = json_request_return_dict("/code/edit/config", method="POST", data = data)
        assert result["success"] == True

    def test_fs_tools(self):
        self.check_OK("/fs_tools")
        self.check_OK("/fs_bookmark")

    def test_create_file(self):
        path = xconfig.DATA_DIR
        resp = json_request_return_dict("/fs_api/add_file", method="POST",
                            data=dict(path=path, filename="test_fs.txt"))
        print(resp)
        self.assertEqual("success", resp["code"])

    def test_create_dir(self):
        path = xconfig.DATA_DIR
        resp = json_request_return_dict(
            "/fs_api/add_dir", 
            method="POST",
            data=dict(path=path, filename="test_fs_dir"))
        print(resp)
        self.assertEqual("success", resp["code"])
    
    def test_code_preview(self):
        self.check_OK("/code/preview?path=./README.md")

    def test_build_fs_index(self):
        size = build_fs_index(xconfig.DATA_DIR, sync=True)
        self.assertTrue(size > 0)

        dao = FileInfoDao()
        info = FileInfo()
        info.fpath = "/data/xxx"
        id1 = dao.save_by_fpath(info)
        id2 = dao.save_by_fpath(info)
        assert id1 == id2
    
    def test_fs_index_manage_page(self):
        path = xutils.quote("./testdata")
        self.check_OK("/fs_index?action=reindex&path={path}".format(path=path), method="POST")
        self.check_OK("/fs_index?p=rebuild")
        self.check_OK("/fs_index")

    def test_config_fs_order(self):
        resp = json_request_return_dict("/fs_api/config", method = "POST", data = dict(action = "sort", order = "size"))
        print(resp)
        self.assertEqual("success", resp["code"])
        
        user_id = xauth.current_user_id()
        self.assertEqual("size", xauth.get_user_config(user_id, "fs_order"))
    
    def test_fs_config_error(self):
        resp = json_request_return_dict("/fs_api/config", method = "POST", data = dict(action = "notfount", order = "size"))
        print(resp)
        self.assertEqual("error", resp["code"])
    
    def test_fs_sidebar(self):
        path = os.getcwd()
        txt_path = get_test_file_path("./fs_preview_test.txt")
        with open(txt_path, "w+") as fp:
            fp.write("test fs preview")

        self.check_OK("/fs_sidebar?path={path}".format(path=path))
        self.check_OK("/fs_preview?path={txt_path}".format(txt_path=txt_path))
        self.check_OK(f"/fs_preview?path={xutils.encode_base64(txt_path)}&b64=true")

        img_resp = request_html(f"/fs_preview?path=test.png")
        assert b"<img" in img_resp

    def test_fs_find(self):
        self.check_OK("/fs_find?key=test")
    
    def test_fs_find_in_cache(self):
        xconfig.USE_CACHE_SEARCH = True
        self.check_OK("/fs_find?key=test")

    def test_fs_upload_search(self):
        self.check_OK("/fs_upload/search?key=" + xutils.quote("test"))

    def test_fs_text(self):
        txt_path = get_test_file_path("./fs_preview_test.txt")
        with open(txt_path, "w+") as fp:
            fp.write("test fs preview")
        self.check_OK(f"/fs_text?method=contents&path={xutils.quote(txt_path)}")
        self.check_OK(f"/fs_text?method=readpage&path={xutils.quote(txt_path)}")
        self.check_OK(f"/fs_text?method=refresh&path={xutils.quote(txt_path)}")

    def test_fs_download(self):
        from xnote_handlers.system.system_sync.dao import SystemSyncTokenDao, SystemSyncToken
        fpath = self.prepare_test_file("./test_download.txt", "test download")
        fpath_b64 = textutil.encode_base64(fpath)
        self.check_OK(f"/fs_download?fpath={fpath_b64}")
        
        xauth.TestEnv.logout()
        try:
            token_info = SystemSyncTokenDao.upsert_by_holder("test", 60)
            self.check_OK(f"/fs_download?fpath={fpath_b64}&token={token_info.token}")
        finally:
            xauth.TestEnv.login_admin()

    def test_file_info(self):
        fpath = self.prepare_test_file("./test_info.txt", "test info")
        user_id = xauth.current_user_id()

        info = FileInfo()
        info.fpath = fpath
        info.user_id = user_id
        file_id = FileInfoDao.save_by_fpath(info)

        self.check_OK(f"/fs_upload/file_info?action=edit&file_id={file_id}")
        data = dict(
            action = "save",
            data = jsonutil.tojson(dict(
                file_id = file_id,
                remark = "update remark",
            ))
        )
        result = json_request_return_dict("/fs_upload/file_info", method="POST", data=data)
        assert result["success"]

        file_info = FileInfoDao.get_by_id(file_id=file_id, user_id=user_id)
        assert file_info != None
        assert file_info.remark == "update remark"
        
    def test_fs_zip(self):
        txt_file = get_test_file_path("./zip.txt")
        zip_file = get_test_file_path("./zip.zip")
        fsutil.writefile(txt_file, "hello,world")
        with ZipFile(zip_file, mode="w") as fp:
            fp.write(txt_file, arcname="zip.txt")
        
        zip_path_b64 = textutil.encode_base64(zip_file)
        self.check_OK(f"/fs/zip/{zip_path_b64}")
        self.check_OK(f"/fs/zip/{zip_path_b64}/zip.txt")