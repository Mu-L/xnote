# encoding=utf-8
# @author xupingmao
# @since 2017
# @modified 2020/11/29 13:51:58
"""
压缩文件，对非ASCII码进行urlencode处理
"""
import zipfile
import os
import sys
from typing import List, Union

def quote_unicode(url: str):
    from xnote.core import xconfig
    if not xconfig.USE_URLENCODE:
        return url
    def quote_char(c):
        # ASCII 范围 [0-127]
        if c <= 127:
            return chr(c)
        return '%%%02X' % c

    bytes = url.encode("utf-8")
    return ''.join([quote_char(c) for c in bytes])


def walk_dir(dirname, skip_hidden=True, filter = None, excluded=[]):
    dirs = []
    files = []
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        if skip_hidden and name.startswith("."):
            continue
        abspath = os.path.abspath(path)
        if abspath in excluded:
            # print("skip", name)
            continue
        if os.path.isdir(path):
            dirs.append(name)
            # yield from 是Python3语法
            # yield from walk_dir(path, skip_hidden)
            for x in walk_dir(path, skip_hidden, filter, excluded):
                yield x
        elif os.path.isfile(path) or os.path.islink(path):
            if filter is not None and not filter(path):
                continue
            files.append(name)
    yield dirname, dirs, files

def get_abs_path_list(dirname, pathlist):
    newpathlist = []
    for path in pathlist:
        fullpath = os.path.join(dirname, path)
        newpathlist.append(os.path.abspath(fullpath))
    return newpathlist


def zip_dir(input_dir: str, outpath: str, skip_hidden=True, filter=None, excluded=[]):
    # 创建目标文件
    absroot = os.path.abspath(outpath)
    # print(absroot)
    with open(outpath, "w"):
        pass
    zf = zipfile.ZipFile(outpath, "w")

    for root, dirs, files in walk_dir(input_dir,
            skip_hidden=skip_hidden, filter=filter,
            excluded=get_abs_path_list(input_dir, excluded)):
        for name in files:
            path = os.path.join(root, name)
            abspath = os.path.abspath(path)
            if abspath == absroot:
                # 跳过目标文件自身
                # print("Skip file", abspath)
                continue
            arcname = path[len(input_dir):]
            zf.write(path, quote_unicode(arcname))
    zf.close()

def is_in_root_dir(zip_info: zipfile.ZipInfo):
    filename = zip_info.filename
    count = filename.count("/")
    if count == 0:
        return True
    
    if count == 1 and filename.endswith("/"):
        # dir in root
        return True
    return False

def _is_child_of(filename: bytes, parent: bytes):
    if filename == parent:
        return False
    
    pos = filename.find(parent)
    if pos < 0:
        return False
    count = filename.count(b"/", pos+len(parent))
    if count == 0:
        return True
    if count == 1 and filename.endswith(b"/"):
        return True
    return False

def _get_filename_bytes(zip_info: zipfile.ZipInfo):
    if zip_info.flag_bits & 0x800:
        # utf-8
        return zip_info.filename.encode("utf-8")
    else:
        # cp437 by zip default
        return zip_info.filename.encode("cp437")
    
    
def is_child_of(zip_info: zipfile.ZipInfo, inner_path: str):
    filename_bytes = _get_filename_bytes(zip_info)
    inner_path_bytes = inner_path.encode("utf-8")
    return _is_child_of(filename_bytes, inner_path_bytes)
        
def find_file_in_zip(zf: zipfile.ZipFile, targetfile: str):
    """注意: 如果targetfile是目录, 需要以/字符结束"""
    targetfile_bytes = targetfile.encode("utf-8")
        
    for zip_info in zf.filelist:
        file_name_bytes = _get_filename_bytes(zip_info)
        if file_name_bytes == targetfile_bytes:
            return zip_info
    return None


if __name__ == '__main__':
    zip_dir(sys.argv[1], sys.argv[2])