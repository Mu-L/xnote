# encoding=utf-8
# @modified 2019/09/30 11:13:34
import os
import web
import xutils
from xnote.core import xtemplate
from xnote.core import xconfig
from xnote.core import xauth
from xnote.core.xtemplate import render
from xutils import Storage
from xutils import fsutil

WIKI_PATH = "./"

HIDE_EXT_LIST = [
    ".bak"
]

def check_resource(path):
    if xutils.is_img_file(path):
        if fsutil.is_parent_dir("./docs", path):
            relative_path = fsutil.get_relative_path(path, "./docs")
            raise web.seeother("/fs_doc?fpath=%s" % xutils.encode_uri_component(relative_path))

        uri = "/fs_get?fpath=%s" % xutils.b64encode(path)
        raise web.seeother(uri)
    return False


class FileItem:

    def __init__(self, parent, name, currentdir):
        if parent.endswith("/"):
            self.path = parent + name
        else:
            self.path = parent + "/" + name
        self.name = name
        fspath = os.path.join(currentdir, name)
        if os.path.isdir(fspath):
            self.type = "dir"
            self.key = "0" + name
        else:
            self.type = "name"
            self.key = "1" + name


def get_path_list(path):
    pathes = path.split("/")
    last = None
    pathlist = []
    for vpath in pathes:
        if vpath == "":
            continue
        if last is not None:
            vpath = last + "/" + vpath
        pathlist.append(vpath)
        last = vpath
    return pathlist


def handle_layout(kw):
    kw.show_aside = False
    embed = xutils.get_argument_bool("embed")
    kw.embed = embed
    if embed:
        kw.show_menu = False
        kw.show_search = False
        kw.show_path = True
        kw.show_nav = False


class PreviewHandler:

    def GET(self, path=""):
        if path == "":
            path = xutils.get_argument_str("path")
        else:
            path = xutils.unquote(path)

        basename = os.path.basename(path)
        path = xconfig.resolve_config_path(path)
        path = xutils.get_real_path(path)
        kw = Storage()

        if os.path.isfile(path):
            check_resource(path)
            type = "file"
            content = xutils.readfile(path)
            assert isinstance(content, str)

            ext = fsutil.get_file_ext(path)
            if ext == "csv" and not content.startswith("```csv"):
                content = "```csv\n" + content + "\n```"
        else:
            # file not exists or not readable
            content = "File \"%s\" does not exists" % path
            type = "file"

        handle_layout(kw)
        kw.html_title = basename
        kw.os = os
        kw.path = path
        kw.content = content
        kw.type = type
        kw.has_readme = False
        
        return render("code/page/preview.html", **kw)


class ReadOnlyHandler:

    def GET(self, path=""):
        realpath = os.path.join(xconfig.TMP_DIR, path)
        content = xutils.readfile(realpath)
        return xtemplate.render("code/page/preview.html",
                                os=os, content=content, type="file")


xurls = (
    r"/code/wiki/(.*)", PreviewHandler,
    r"/code/wiki", PreviewHandler,
    r"/code/preview", PreviewHandler
)
