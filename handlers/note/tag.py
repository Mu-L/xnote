# encoding=utf-8
# Created by xupingmao on 2017/04/16
# @modified 2019/04/25 22:12:02
import math
import xutils
import xtemplate
import xauth
import xtables
import xconfig

class TagHandler:
    
    def GET(self, id):
        id        = int(id)
        db        = xtables.get_file_tag_table()
        user_name = xauth.get_current_name()
        sql = "SELECT * FROM file_tag WHERE file_id=$file_id AND (user=$user OR is_public=1)"
        file_tags = db.query(sql, vars=dict(file_id=id, user=user_name))
        return dict(code="", message="", data=list(file_tags))

class UpdateTagHandler:

    @xauth.login_required()
    def POST(self):
        from . import dao
        id       = xutils.get_argument("file_id", type=int)
        tags_str = xutils.get_argument("tags")
        tag_db   = xtables.get_file_tag_table()
        user_name = xauth.get_current_name()
        
        if tags_str is None or tags_str == "":
            tag_db.delete(where=dict(file_id=id, user=user_name))
            return dict(code="success")
        new_tags = set(tags_str.split(" "))
        file     = dao.get_by_id(id)
        db       = dao.get_file_db()
        file_db  = xtables.get_file_table()
        # 求出两个差集进行运算
        old_tags = tag_db.select(where=dict(file_id=id, user=user_name))
        old_tags = set([v.name for v in old_tags])

        to_delete = old_tags - new_tags
        to_add    = new_tags - old_tags

        for item in to_delete:
            tag_db.delete(where=dict(name=item, file_id=id, user=user_name))
        for item in to_add:
            if item == "": continue
            tag_db.insert(name=item, file_id=id, user=user_name, is_public=file.is_public)

        file_db.update(related=tags_str, where=dict(id=id))
        return dict(code="", message="", data="OK")

    def GET(self):
        return self.POST()

class TagNameHandler:

    def GET(self, tagname):
        from . import dao
        tagname  = xutils.unquote(tagname)
        db       = xtables.get_file_table()
        page     = xutils.get_argument("page", 1, type=int)
        limit    = xutils.get_argument("limit", 10, type=int)
        offset   = (page-1) * limit
        pagesize = xconfig.PAGE_SIZE

        if xauth.has_login():
            user_name = xauth.get_current_name()
        else:
            user_name = ""
        count_sql = "SELECT COUNT(1) AS amount FROM file_tag WHERE LOWER(name) = $name AND (user=$user OR is_public=1)"
        sql = "SELECT f.* FROM file f, file_tag ft ON ft.file_id = f.id WHERE LOWER(ft.name) = $name AND (ft.user=$user OR ft.is_public=1) ORDER BY f.ctime DESC LIMIT $offset, $limit"
        count = db.query(count_sql, vars=dict(name=tagname.lower(), user=user_name))[0].amount

        files = db.query(sql,
            vars=dict(name=tagname.lower(), offset=offset, limit=limit, user=user_name))
        files = [dao.FileDO.fromDict(f) for f in files]
        return xtemplate.render("note/tagname.html", 
            show_aside = True,
            tagname    = tagname, 
            files      = files, 
            show_mdate = True,
            page_max   = math.ceil(count / pagesize), 
            page       = page)


class TagListHandler:

    def GET(self):
        if xauth.has_login():
            user_name = xauth.get_current_name()
            tag_list  = xutils.call("note.list_tag", user_name)
        else:
            tag_list  = xutils.call("note.list_tag", "")
        return xtemplate.render("note/taglist.html", 
            show_aside = True,
            tag_list = tag_list)

xurls = (
    r"/note/tag/(\d+)"   , TagHandler,
    r"/note/tag/update"  , UpdateTagHandler,
    r"/note/tagname/(.*)", TagNameHandler,
    r"/note/taglist"     , TagListHandler
)

