# -*- coding:utf-8 -*-
# @author xupingmao
# @since 2017
# @modified 2020/02/16 13:04:38

"""笔记编辑相关处理"""
import os
import web
import time
import xauth
import xutils
import xtemplate
import xtables
import xmanager
import xconfig
from xutils import Storage
from xutils import dateutil
from xutils import cacheutil
from xutils import dbutil
from xutils import textutil
from xtemplate import T
from .constant import *
NOTE_DAO = xutils.DAO("note")

class NoteException(Exception):

    def __init__(self, code, message):
        super(NoteException, self).__init__(message)
        self.code = code
        self.message = message

@xmanager.listen(["note.add", "note.updated", "note.rename", "note.remove"])
def update_note_cache(ctx):
    type = ctx.get("type", "")
    cacheutil.prefix_del("[%s]note" % xauth.get_current_name())

@xmanager.listen("note.updated")
def record_history(ctx):
    id      = ctx.get("id")
    content = ctx.get("content")
    version = ctx.get("version")
    mtime   = ctx.get("mtime")
    name    = ctx.get("name")
    NOTE_DAO.add_history(id, version, ctx)

def get_heading_by_type(type):
    title = u"创建" + NOTE_TYPE_DICT.get(type, u"笔记")
    return T(title)

def fire_update_event(note):
    event_body = dict(id=note.id, 
            name = note.name, 
            mtime = dateutil.format_datetime(), 
            content = note.content, 
            version = note.version+1)
    xmanager.fire('note.updated', event_body)

def fire_rename_event(note):
    event_body = dict(action = "rename", id = note.id, name = note.name, type = note.type)
    xmanager.fire("note.rename", event_body)

def create_log_func(note, ctx):
    date_str  = time.strftime("%Y.%m.%d")
    note.name = u"日志:" + date_str + dateutil.current_wday()
    return NOTE_DAO.create(note)

def default_create_func(note, ctx):
    method = ctx.method
    name   = note.name

    if method != "POST":
        # GET请求直接返回
        return

    if name == '':
        message = u'标题为空'
        raise Exception(message)

    f = NOTE_DAO.get_by_name(note.creator, name)
    if f != None:
        message = u"%s 已存在" % name
        raise Exception(message)
    return NOTE_DAO.create(note)

CREATE_FUNC_DICT = {
    "log": create_log_func
}

class CreateHandler:

    @xauth.login_required()
    def POST(self, method='POST'):
        name      = xutils.get_argument("name", "")
        tags      = xutils.get_argument("tags", "")
        key       = xutils.get_argument("key", "")
        content   = xutils.get_argument("content", "")
        type      = xutils.get_argument("type", "md")
        format    = xutils.get_argument("_format", "")
        parent_id = xutils.get_argument("parent_id", "0")

        if key == "":
            key = time.strftime("%Y.%m.%d") + dateutil.current_wday()

        type = NOTE_TYPE_MAPPING.get(type, type)

        creator        = xauth.current_name()
        note           = Storage(name = name)
        note.atime     = xutils.format_datetime()
        note.mtime     = xutils.format_datetime()
        note.ctime     = xutils.format_datetime()
        note.creator   = creator
        note.parent_id = parent_id
        note.type      = type
        note.content   = content
        note.data      = ""
        note.size      = len(content)
        note.is_public = 0
        note.priority  = 0
        note.version   = 0
        note.is_deleted = 0
        note.tags       = textutil.split_words(tags)

        heading = T("创建笔记")
        code = "fail"
        error = ""
        ctx = Storage(method = method)
        
        try:
            if type not in VALID_NOTE_TYPE_SET:
                raise Exception(u"无效的类型: %s" % type)

            create_func = CREATE_FUNC_DICT.get(type, default_create_func)
            inserted_id = create_func(note, ctx)
            if format == "json":
                return dict(code="success", id = inserted_id, url = "/note/edit?id=%s" % inserted_id)
            if inserted_id != None:
                raise web.seeother("/note/edit?id={}".format(inserted_id))
        except web.HTTPError as e1:
            xutils.print_exc()
            raise e1
        except Exception as e:
            xutils.print_exc()
            error = xutils.u(e)
            if format == 'json':
                return dict(code = 'fail', message = error)

        heading = get_heading_by_type(type)

        return xtemplate.render("note/page/create.html", 
            show_search = False,
            heading  = heading,
            key      = "", 
            type     = type,
            name     = key, 
            tags     = tags, 
            error    = error,
            message  = error,
            NOTE_TYPE_LIST = NOTE_TYPE_LIST,
            groups   = NOTE_DAO.list_group(creator),
            code     = code)

    def GET(self):
        return self.POST('GET')

class AddHandler(CreateHandler):
    pass


class RemoveAjaxHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id", "")
        name = xutils.get_argument("name", "")
        file = None

        if id != "" and id != None:
            file = NOTE_DAO.get_by_id(id)
        elif name != "":
            file = NOTE_DAO.get_by_name(xauth.current_name(), name)
        else:
            return dict(code="fail", message="id,name至少一个不为空")

        if file is None:
            return dict(code="fail", message="笔记不存在")

        creator = xauth.current_name()
        if not xauth.is_admin() and file.creator != creator:
            return dict(code="fail", message="没有删除权限")

        if file.type == "group":
            children_count = NOTE_DAO.count_by_parent(creator, file.id)
            if children_count > 0:
                return dict(code="fail", message="分组不为空")

        NOTE_DAO.delete(file.id)
        return dict(code="success")
        
    def POST(self):
        return self.GET()


class RenameAjaxHandler:

    @xauth.login_required()
    def POST(self):
        id   = xutils.get_argument("id")
        name = xutils.get_argument("name")
        if name == "" or name is None:
            return dict(code="fail", message="名称为空")

        old = NOTE_DAO.get_by_id(id)
        if old is None:
            return dict(code="fail", message="笔记不存在")

        if old.creator != xauth.get_current_name():
            return dict(code="fail", message="没有权限")

        file = NOTE_DAO.get_by_name(xauth.current_name(), name)
        if file is not None and file.is_deleted == 0:
            return dict(code="fail", message="%r已存在" % name)

        NOTE_DAO.update(id, name=name)

        fire_update_event(old)
        fire_rename_event(old)

        return dict(code="success")

    def GET(self):
        return self.POST()
    
class PublicShareHandler:

    @xauth.login_required()
    def GET(self):
        id      = xutils.get_argument("id")
        note    = check_get_note(id)
        NOTE_DAO.update(id, is_public = 1)
        raise web.seeother(note.url)

class LinkShareHandler:

    @xauth.login_required()
    def POST(self):
        id   = xutils.get_argument("id")
        note = check_get_note(id)
        if note.token != None:
            return dict(code = "success", data = "/note/view?token=%s" % note.token)
        else:
            token = NOTE_DAO.create_token("note", note.id)
            NOTE_DAO.update(note.id, token = token)
        return dict(code = "success", data = "/note/view?token=%s" % token)

class UnshareHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, is_public = 0)
        raise web.seeother(note.url)

def check_get_note(id):
    if xauth.is_admin():
        note = NOTE_DAO.get_by_id(id)
    else:
        note = NOTE_DAO.get_by_id_creator(id, xauth.current_name())

    if note is None:
        raise NoteException("404", "笔记不存在")
    return note

def update_and_notify(file, update_kw):
    rowcount = NOTE_DAO.update(file.id, **update_kw)
    if rowcount > 0:
        fire_update_event(file)
    else:
        # 更新冲突了
        raise NoteException("409", "更新失败")

class SaveAjaxHandler:

    @xauth.login_required()
    def POST(self):
        content = xutils.get_argument("content", "")
        data    = xutils.get_argument("data", "")
        id      = xutils.get_argument("id")
        type    = xutils.get_argument("type")
        version = xutils.get_argument("version", 0, type=int)
        name    = xauth.get_current_name()
        where   = None

        try:
            file = check_get_note(id)
            kw = dict(size = len(content), 
                mtime = xutils.format_datetime(), 
                version = version + 1)

            if type == "html":
                kw["data"]    = data
                kw["content"] = data
                if xutils.bs4 is not None:
                    soup          = xutils.bs4.BeautifulSoup(data, "html.parser")
                    content       = soup.get_text(separator=" ")
                    kw["content"] = content
                kw["size"] = len(content)
            else:
                kw["content"] = content
                kw['data']    = ''
                kw["size"]    = len(content)

            update_and_notify(file, kw)
            return dict(code = "success")
        except NoteException as e:
            return dict(code = "fail", message = e.message)

class UpdateHandler:

    @xauth.login_required()
    def POST(self):
        is_public = xutils.get_argument("public", "")
        id        = xutils.get_argument("id")
        content   = xutils.get_argument("content")
        version   = xutils.get_argument("version", 0, type=int)
        file_type = xutils.get_argument("type")
        name      = xutils.get_argument("name", "")

        try:
            file = check_get_note(id)

            # 理论上一个人是不能改另一个用户的存档，但是可以拷贝成自己的
            # 所以权限只能是创建者而不是修改者
            update_kw = dict(content=content, 
                    type = file_type, 
                    size = len(content),
                    version = version);
            if name != "" and name != None:
                update_kw["name"] = name
            # 更新并且发出消息
            update_and_notify(file, update_kw)
            raise web.seeother("/note/%s" % id)
        except NoteException as e:
            return xtemplate.render("note/page/view.html", 
                pathlist = [],
                file     = file, 
                content  = content, 
                error    = e.message)

class StickHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, priority = 1, archived = False)
        raise web.found("/note/%s" % id)

class UnstickHandler:
    
    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, priority = 0)
        raise web.found("/note/%s" % id)

class ArchiveHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, archived=True, priority = -1)
        raise web.found("/note/%s" % id)

class ResetHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, archived=False, priority = 0)
        raise web.found(note.url)

class UnarchiveHandler:

    @xauth.login_required()
    def GET(self):
        id = xutils.get_argument("id")
        note = check_get_note(id)
        NOTE_DAO.update(id, archived=False)
        raise web.found("/note/%s" % id)

class MoveAjaxHandler:
    
    @xauth.login_required()
    def GET(self):
        id        = xutils.get_argument("id", "")
        parent_id = xutils.get_argument("parent_id", "")
        file = NOTE_DAO.get_by_id_creator(id, xauth.current_name())
        if file is None:
            return dict(code="fail", message="笔记不存在")
        if str(id) == str(parent_id):
            return dict(code="fail", message="不能移动到自身目录")

        NOTE_DAO.move(file, parent_id)
        return dict(code="success")

    def POST(self):
        return self.GET()

class AppendAjaxHandler:

    def GET(self):
        return self.POST()

    @xauth.login_required()
    def POST(self):
        user    = xauth.current_name()
        note_id = xutils.get_argument("note_id")
        content = xutils.get_argument("content")
        version = xutils.get_argument("version", 1, type = int)
        note = NOTE_DAO.get_by_id(note_id)

        if note == None:
            return dict(code = "404", message = "note not found")

        if note.creator != user:
            return dict(code = "403", message = "unauthorized")

        if note.list_items is None:
            note.list_items = []
        note.list_items.append(content)
        NOTE_DAO.update0(note)

        fire_update_event(note)
        return dict(code = "success")
        

xurls = (
    r"/note/add"         , AddHandler,
    r"/note/create"      , CreateHandler,
    r"/note/remove"      , RemoveAjaxHandler,
    r"/note/rename"      , RenameAjaxHandler,
    r"/note/update"      , UpdateHandler,
    r"/note/save"        , SaveAjaxHandler,
    r"/note/append"      , AppendAjaxHandler,
    r"/note/stick"       , StickHandler,
    r"/note/archive"     , ArchiveHandler,
    r"/note/reset"       , ResetHandler,
    r"/note/move"        , MoveAjaxHandler,
    r"/note/group/move"  , MoveAjaxHandler,

    r"/note/unstick"     , UnstickHandler,
    r"/note/unarchive"   , UnarchiveHandler,
    
    # 分享
    r"/note/share",        PublicShareHandler,
    r"/note/share/public", PublicShareHandler,
    r"/note/share/cancel", UnshareHandler,
    r"/note/link_share",   LinkShareHandler,

    r"/file/save"        , SaveAjaxHandler,
    r"/file/autosave"    , SaveAjaxHandler
)


