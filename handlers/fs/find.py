# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2017/??/??
# @modified 2018/10/25 02:26:51
import os
import glob
import xutils
import xauth
import xtemplate
import xconfig
from fnmatch import fnmatch

@xutils.cache(key="fs.list", expire=-1)
def get_cached_files():
    count = 0
    file_cache = []
    for root, dirs, files in os.walk(xconfig.DATA_DIR):
        for item in dirs:
            path = os.path.join(root, item)
            file_cache.append(path)
            count += 1
        for item in files:
            path = os.path.join(root, item)
            file_cache.append(path)
            count += 1
    xutils.log("files count = {}", count)
    return file_cache

def find_in_cache0(key):
    key = key.upper()
    plist = []
    files = get_cached_files()
    for item in files:
        if fnmatch(item.upper(), key):
            plist.append(item)
    return plist

def find_in_cache(key):
    quoted_key = xutils.quote_unicode(key)
    plist = find_in_cache0(key)
    if quoted_key != key:
        plist += find_in_cache0(quoted_key)
    return plist

class handler:

    def GET(self):
        return self.POST()

    @xauth.login_required("admin")
    def POST(self):
        path = xutils.get_argument("path")
        find_key = xutils.get_argument("find_key", "")
        find_type = xutils.get_argument("type")
        mode = xutils.get_argument("mode")
        if find_key == "" or find_key is None:
            find_key = xutils.get_argument("key", "")
        find_key = "*" + find_key + "*"
        path_name = os.path.join(path, find_key)
        if find_key == "**":
            plist = []
        elif os.path.abspath(path) == os.path.abspath(xconfig.DATA_DIR) and xconfig.USE_CACHE_SEARCH:
            # search in cache
            plist = find_in_cache(find_key)
        else:
            plist = xutils.search_path(path, find_key)
        # TODO max result size
        tpl = "fs/fs.html"
        if mode == "grid":
            tpl = "fs/fs_grid.html"
        return xtemplate.render(tpl, 
            token = xauth.get_current_user().token,
            filelist = [xutils.FileItem(p, path) for p in plist])

xurls = (
    r"/fs_find", handler
)
