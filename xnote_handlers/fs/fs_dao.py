
import os
from xnote.core import xconfig, xtables
from xutils import fsutil, textutil
from .fs_models import FileInfo


class FileInfoDao:
    
    data_root = xconfig.FileReplacement.data_dir + "/"
    db = xtables.get_table_by_name("file_info")
    
    @classmethod
    def get_virtual_path(cls, fpath=""):
        if fpath.startswith(cls.data_root):
            return fpath
        data_dir = xconfig.FileConfig.data_dir
        fpath = os.path.abspath(fpath)
        if fsutil.is_parent_dir(data_dir, fpath):
            relative_path = fsutil.get_relative_path(fpath, data_dir)
            fpath = cls.data_root + relative_path
        return fpath

    @classmethod
    def get_by_fpath(cls, fpath = ""):
        fpath = cls.get_virtual_path(fpath)
        result = cls.db.select_first(where = dict(fpath = fpath))
        return FileInfo.from_dict_or_None(result)
    
    @classmethod
    def get_by_id(cls, file_id=0, user_id=0):
        return FileInfo.from_dict_or_None(cls.db.select_first(where = dict(id = file_id, user_id=user_id)))
    
    @classmethod
    def get_by_sha256(cls, user_id=0, sha256=""):
        assert user_id > 0
        assert len(sha256) > 0
        result = cls.db.select_first(where = dict(user_id=user_id, sha256=sha256))
        return FileInfo.from_dict_or_None(result)
    
    @classmethod
    def delete_by_fpath(cls, fpath=""):
        fpath = cls.get_virtual_path(fpath)
        return cls.db.delete(where=dict(fpath=fpath))
    
    @classmethod
    def delete_by_id(cls, id=0):
        return cls.db.delete(where=dict(id=id))
    
    @classmethod
    def save_by_fpath(cls, info: FileInfo):
        info.fpath = cls.get_virtual_path(info.fpath)
        old = cls.get_by_fpath(info.fpath)
        if old == None:
            save_dict = info.to_save_dict()
            new_id = int(cls.db.insert(**save_dict)) # type: ignore
            info.id = new_id
            return new_id
        else:
            info.id = old.id
            save_dict = info.to_save_dict()
            cls.db.update(**save_dict, where = dict(id=old.id))
            return info.id

    @classmethod
    def replace(cls, info: FileInfo):
        info.fpath = cls.get_virtual_path(info.fpath)
        save_dict = info.to_replace_dict()
        cls.db.replace(**save_dict)

    @classmethod
    def save(cls, info: FileInfo):
        info.fpath = cls.get_virtual_path(info.fpath)
        if info.id > 0:
            cls.db.update(where=dict(id=info.id), **info.to_save_dict())
            return info.id
        else:
            save_dict = info.to_save_dict()
            return cls.db.insert(**save_dict)

    @classmethod
    def list(cls, user_id=0, offset=0, limit=100, 
             start_time_inclusive="", end_time_exclusive="", 
             is_admin=False, order="ctime desc"):
        rows, _ = cls.query_page(
            user_id=user_id, offset=offset, limit=limit, 
            start_time_inclusive=start_time_inclusive, 
            end_time_exclusive=end_time_exclusive, is_admin=is_admin, order=order, 
            do_count=False)
        return rows

    @classmethod 
    def query_page(cls, user_id=0, offset=0, limit=100, 
             start_time_inclusive="", end_time_exclusive="", 
             is_admin=False, order="ctime desc", do_count = True):
        if not is_admin:
            assert user_id > 0
        vars = dict(user_id=user_id, start_time_inclusive=start_time_inclusive, 
                    end_time_exclusive=end_time_exclusive)
        where = "1=1"
        if user_id != 0:
            where += " AND user_id=$user_id"
        if start_time_inclusive != "":
            where += " AND ctime >= $start_time_inclusive"
        if end_time_exclusive != "":
            where += " AND ctime < $end_time_exclusive"
        if do_count:
            count = cls.db.count(where=where, vars=vars)
        else:
            count = 0

        result = cls.db.select(where=where, vars=vars, offset=offset, limit=limit, order=order)
        return FileInfo.from_dict_list(result), count

    @classmethod
    def prefix_count(cls, fpath=""):
        if fpath != "":
            fpath = cls.get_virtual_path(fpath)
        return cls.db.count(where = "fpath LIKE $fpath", vars = dict(fpath = fpath + "%"))
    
    @classmethod
    def list_next_batch(cls, last_id=0, limit=20):
        where = "id > $id"
        vars = dict(id = last_id)
        file_info_list = cls.db.select(where=where, vars=vars, order="id", offset=0, limit=limit)
        return FileInfo.from_dict_list(file_info_list)
    
    @classmethod
    def get_max_id(cls):
        record = cls.db.select_first(order="id desc")
        if record is None:
            return 0
        return FileInfo.from_dict(record).id
    
    @classmethod
    def search(cls, user_id=0, search_key="", limit = 50, order = "ctime desc"):
        words = textutil.split_words(search_key)
        remark_like = '%' + '%'.join(words) + '%'

        where = "user_id=$user_id AND remark LIKE $remark_like"
        vars = dict(user_id=user_id, remark_like = remark_like)
        return FileInfo.from_dict_list(cls.db.select(where=where, vars=vars, limit=limit, order=order))
