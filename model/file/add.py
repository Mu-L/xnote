from BaseHandler import *
import FileDB
from FileDB import FileDO

import xauth

class handler(BaseHandler):

    def execute(self):
        name = self.get_argument("name", "")
        tags = self.get_argument("tags", "")
        key  = self.get_argument("key", "")
        type = self.get_argument("type", "md")

        file = FileDO(name)
        file.atime = dateutil.get_seconds()
        file.satime = dateutil.format_time()
        file.mtime = dateutil.get_seconds()
        file.smtime = dateutil.format_time()
        file.ctime = dateutil.get_seconds()
        file.sctime = dateutil.format_time()
        file.creator = xauth.get_current_user()["name"]
        file.groups = file.creator
        file.parent_id = 0
        file.type = type
        error = ""
        try:
            if name != '':
                f = FileDB.insert(file)
                inserted = FileDB.get_by_name(name)
                raise web.seeother("/file/edit?id=%s" % inserted.id)
        except Exception as e:
            error = e
        self.render("file/add.html", key = "", name = key, tags = tags, error=error)