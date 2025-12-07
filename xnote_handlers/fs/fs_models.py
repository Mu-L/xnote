import xutils
from xnote.core import xconfig, xtables
from xutils import BaseDataRecord
from xutils import Storage
from xutils import fsutil

class FileInfoRecord(BaseDataRecord):

    def __init__(self):
        self.id = 0
        self.ctime = xutils.format_datetime()
        self.mtime = xutils.format_datetime()
        self.fpath = ""
        self.ftype = ""
        self.user_id = 0
        self.fsize = 0
        self.remark = ""
        self.sha256 = ""

    def to_replace_dict(self):
        result = dict(**self)
        if self.id == 0:
            result.pop("id")
        return result

    def to_save_dict(self):
        result = dict(**self)
        result.pop("id")
        if self.id != 0:
            # 更新操作
            result.pop("ctime", None) # 不更新创建时间
            result.pop("user_id", None)
        if self.remark == "":
            # 不更新remark的空值
            result.pop("remark", None)
        return result

    @property
    def realpath(self):
        return self.fpath.replace(xconfig.FileReplacement.data_dir, xconfig.FileConfig.data_dir)
    
    def to_file_index_info(self):
        result = FileIndexInfo()
        result.id = self.id
        result.fpath = self.fpath
        result.mtime = self.mtime
        result.user_id = self.user_id
        result.fsize = self.fsize
        result.ftype = self.ftype
        result.sha256 = self.sha256
        result.sha1_sum = fsutil.get_sha1_sum(self.realpath)
        return result

FileInfo = FileInfoRecord


class FileIndexInfo(BaseDataRecord):
    """文件索引信息 (用于数据同步) """
    def __init__(self, **kw):
        self.id = 0
        self.webpath = ""
        self.fpath = ""
        self.mtime = xtables.DEFAULT_DATETIME
        self.user_id = 0
        self.fsize = 0
        self.ftype = ""
        self.last_try_time = 0.0
        self.exists = True # 默认存在
        self.sha1_sum = ""
        self.sha256 = ""
        self.update(kw)

    @property
    def realpath(self):
        return self.fpath.replace(xconfig.FileReplacement.data_dir, xconfig.FileConfig.data_dir)