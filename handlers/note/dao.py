# encoding=utf-8
# Created by xupingmao on 2017/04/16
# @modified 2018/12/08 00:12:11

"""资料的DAO操作集合

由于sqlite是单线程，所以直接使用方法操作
如果是MySQL等数据库，使用 threadeddict 来操作，直接用webpy的ctx
"""
import time
import math
import re
import six
import web.db as db
import xconfig
import xtables
import xutils
import xauth
from xutils import readfile, savetofile, sqlite3
from xutils import dateutil, cacheutil, Timer

MAX_VISITED_CNT = 200
readFile        = readfile
config          = xconfig
DB_PATH         = config.DB_PATH


class FileDO(dict):
    """This class behaves like both object and dict"""
    def __init__(self, name):
        self.id          = None
        self.related     = ''
        self.size        = 0
        t                = dateutil.get_seconds()
        self.mtime       = t
        self.atime       = t
        self.ctime       = t
        self.visited_cnt = 0
        self.name        = name

    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError as k:
            # raise AttributeError(k)
            return None
    
    def __setattr__(self, key, value): 
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)
    
    @staticmethod
    def fromDict(dict, option=None):
        """build fileDO from dict"""
        name = dict['name']
        file = FileDO(name)
        for key in dict:
            file[key] = dict[key]
            # setattr(file, key, dict[key])
        if file.get("content", None) is None:
            file.content = ""
        if option:
            file.option = option
        file.url = "/note/view?id={}".format(dict["id"])
        return file

def query_note_conent(id):
    db = xtables.get_note_content_table()
    result = db.select_one(where=dict(id=id))
    if result is None:
        return None, None
    return result.get("content", ""), result.get("data", "")

def build_note(dict):
    id   = dict['id']
    name = dict['name']
    note = FileDO(name)
    for key in dict:
        note[key] = dict[key]
        # setattr(file, key, dict[key])
    if note.get("content", None) is None:
        note.content = ""
    content, data = query_note_conent(id)
    if content is not None:
        note.content = content
    if data is not None:
        note.data = data
    note.url = "/note/view?id={}".format(dict["id"])
    return note


def to_sqlite_obj(text):
    if text is None:
        return "NULL"
    if not isinstance(text, six.string_types):
        return repr(text)
    text = text.replace("'", "''")
    return "'" + text + "'"


class TableDesc:
    def __init__(self, row = None):
        if row != None:
            self.name = row[0]
            self.items = []
        else:
            self.name = ""
            self.items = []
    
    def __repr__(self):
        return "%s :{\n%s\n}" % (self.name, self.items)

class RowDesc:
    def __init__(self, row):
        self.name = row['name']
        self.type = row['type']
        self.defaultValue = row['dflt_value']
        self.notNull = row['notnull']
        self.primaryKey = row['pk']

    def __repr__(self):
        return "%s : %s\n" % (self.name, self.type)


def get_file_db():
    return xtables.get_file_table()

def get_pathlist(db, file, limit = 2):
    pathlist = []
    while file is not None:
        pathlist.insert(0, file)
        file.url = "/note/view?id=%s" % file.id
        if len(pathlist) >= limit:
            break
        if file.parent_id == 0:
            break
        else:
            file = db.select_one(what="id,name,type,creator", where=dict(id=file.parent_id))
    return pathlist

def get_by_id(id, db=None):
    if db is None:
        db = get_file_db()
    first = db.select_one(where=dict(id=id))
    if first is not None:
        return build_note(first)
    return None

def get_by_name(name, db=None):
    if db is None:
        db = get_file_db()
    result = get_db().select_one(where=dict(name=name, is_deleted=0))
    if result is None:
        return None
    return build_note(result)

def get_vpath(record):
    pathlist = []
    current = record
    db = FileDB()
    while current is not None:
        pathlist.append(current)
        if current.parent_id is not None and current.parent_id != "":
            current = get_by_id(current.parent_id, db)
        else:
            current = None

    pathlist.reverse()
    return pathlist

def visit_by_id(id, db = None):
    sql = "UPDATE file SET visited_cnt = visited_cnt + 1, atime='%s' where id = %s " % \
        (dateutil.format_time(), id)
    return db.query(sql)

def get_recent_visit(count):
    db = FileDB()
    all = db.execute("SELECT * from file where is_deleted != 1 and not (related like '%%HIDE%%') order by atime desc limit %s" % count)
    return [FileDO.fromDict(item) for item in all]

def get_recent_created(count):
    db = FileDB()
    all = db.execute("SELECT * FROM file WHERE is_deleted != 1 ORDER BY ctime DESC LIMIT %s" % count)
    return [FileDO.fromDict(item) for item in all]

def get_recent_modified(count):
    db = FileDB()
    all = db.execute("SELECT * FROM file WHERE is_deleted != 1 ORDER BY mtime DESC LIMIT %s" % count)
    return [FileDO.fromDict(item) for item in all]

def update(where, **kw):
    db = get_file_db()
    kw["mtime"] = dateutil.format_time()
    # 处理乐观锁
    version = where.get("version")
    if version:
        kw["version"] = version + 1
    return db.update(where = where, vars=None, **kw)

def update_children_count(parent_id, db=None):
    if parent_id is None or parent_id == "":
        return
    if db is None:
        db = get_file_db()
    group_count = db.count(where="parent_id=$parent_id AND is_deleted=0", vars=dict(parent_id=parent_id))
    db.update(size=group_count, where=dict(id=parent_id))

def delete_by_id(id):
    update(where=dict(id=id), is_deleted=1)

def insert(file):
    name = file.name
    f = get_by_name(name)
    if f is not None:
        raise FileExistsError(name)
    if not hasattr(file, "is_deleted"):
        file.is_deleted = 0
    return get_db().insert(**file)
        
def get_db():
    return get_file_db()


def build_sql_row(obj, k):
    v = getattr(obj, k)
    if v is None: return 'NULL'
    return to_sqlite_obj(v)

def get_table_struct(table_name):
    rs = get_db().execute("pragma table_info('%s')" % table_name)
    result = []
    for item in rs:
        result.append(item)
    return result

def list_group(current_name = None):
    if current_name is None:
        current_name = str(xauth.get_current_name())
    t1 = time.time()
    cache_key = "[%s]note.group.list" % current_name
    value = cacheutil.get(cache_key)
    if value is None:
        sql = "SELECT * FROM file WHERE type = 'group' AND is_deleted = 0 AND creator = $creator ORDER BY name LIMIT 1000"
        value = list(xtables.get_file_table().query(sql, vars = dict(creator=current_name)))
        cacheutil.set(cache_key, value, expire=600)
    t2 = time.time()
    xutils.trace("NoteDao.ListGroup", "", int((t2-t1)*1000))
    return value

def list_recent_created(parent_id = None, limit = 10):
    t = Timer()
    t.start()
    where = "is_deleted = 0 AND (creator = $creator)"
    if parent_id != None:
        where += " AND parent_id = %s" % parent_id
    db = xtables.get_file_table()
    result = list(db.select(where = where, 
            vars   = dict(creator = xauth.get_current_name()),
            order  = "ctime DESC",
            limit  = limit))
    t.stop()
    xutils.trace("NoteDao.ListRecentCreated", "", t.cost_millis())
    return result

def list_recent_edit(parent_id=None, offset=0, limit=None):
    if limit is None:
        limit = xconfig.PAGE_SIZE
    db = xtables.get_file_table()
    t = Timer()
    t.start()
    creator = xauth.get_current_name()
    where = "is_deleted = 0 AND (creator = $creator) AND type != 'group'"
    
    cache_key = "[%s]note.recent#%s" % (creator, math.ceil(offset/limit))
    files = cacheutil.get(cache_key)
    if files is None:
        files = list(db.select(what="name, id, parent_id, ctime, mtime, type, creator", 
            where = where, 
            vars   = dict(creator = creator),
            order  = "mtime DESC",
            offset = offset,
            limit  = limit))
        cacheutil.set(cache_key, files, expire=600)
    t.stop()
    xutils.trace("NoteDao.ListRecentEdit", "", t.cost_millis())
    return files

def count_recent_edit(creator):
    t = Timer()
    t.start()
    count_key = "[%s]note.count" % creator
    count = cacheutil.get(count_key)
    if count is None:
        db    = xtables.get_file_table()
        where = "is_deleted = 0 AND creator = $creator AND type != 'group'"
        count = db.count(where, vars = dict(creator = xauth.get_current_name()))
        cacheutil.set(count_key, count, expire=600)
    t.stop()
    xutils.trace("NoteDao.CountRecentEdit", "", t.cost_millis())
    return count

xutils.register_func("note.list_group", list_group)
xutils.register_func("note.list_recent_created", list_recent_created)
xutils.register_func("note.list_recent_edit", list_recent_edit)
xutils.register_func("note.count_recent_edit", count_recent_edit)

