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

from zipfile import ZipInfo
from typing import List, Union, Optional, Dict


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


def walk_dir(dirname, skip_hidden=True, filter=None, excluded=[]):
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

    for root, dirs, files in walk_dir(
            input_dir, skip_hidden=skip_hidden, filter=filter, 
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


def _fix_zip_filename(filename: str):
    """
    修复 ZIP 文件中乱码的文件名
    :param filename: zipfile 读取的原始乱码文件名
    :return: 解码后的正确文件名
    """
    # 步骤1：先尝试 UTF-8 解码（新版 ZIP 优先）
    try:
        return filename.encode('cp437').decode('utf-8')
    except UnicodeDecodeError:
        pass

    # 步骤2：尝试 GBK/GB2312 解码（Windows 老版 ZIP）
    try:
        return filename.encode('cp437').decode('gbk')
    except UnicodeDecodeError:
        pass

    # 步骤3：兜底（替换无法解码的字符）
    return filename.encode('cp437').decode('utf-8', errors='replace')


def _get_filename_str(zip_info: zipfile.ZipInfo):
    if zip_info.flag_bits & 0x800:
        # utf-8
        return zip_info.filename
    else:
        # cp437 by zip default
        return _fix_zip_filename(zip_info.filename)


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


class ZipFileTreeNode:
    # 相对zip的路径, 等同于zip_info.filename
    path: str

    def __init__(
        self, zip_info: Optional[ZipInfo],
        name: str,
        parent: Optional["ZipFileTreeNode"],
        root: Optional["ZipFileTreeRoot"]
    ):
        # 函数定义分隔符
        self.zip_info = zip_info
        self.children: List["ZipFileTreeNode"] = []
        self.name = name
        self.is_dir = True
        self.parent = parent
        self.path = ""

        if zip_info:
            self.is_dir = zip_info.is_dir()

        if parent is None:
            if name != "":
                raise Exception("only root node can have empty parent")
        else:
            assert root != None
            parent_path = parent.path
            if parent_path == "" or parent_path == "/":
                self.path = name
            else:
                self.path = parent_path + "/" + name
            parent.children.append(self)
            root.file_dict[self.path] = self

    def find_child(self, name: str):
        for item in self.children:
            if item.name == name:
                return item
        return None

    def find_dir(self, dirname: str, root: "ZipFileTreeRoot"):
        names = dirname.split("/")
        cwd = self
        for name in names:
            if name == "":
                continue
            child = cwd.find_child(name)
            if child is None:
                child = ZipFileTreeNode(None, name, cwd, root)
            cwd = child
        return cwd

    def print_tree(self, indent=0):
        print((" " * indent) +
              f"name={self.name}, is_dir={self.is_dir}, children.size={len(self.children)}")
        for child in self.children:
            child.print_tree(indent+2)


class ZipFileTreeRoot(ZipFileTreeNode):
    def __init__(self):
        super().__init__(None, "", None, None)
        # only root node has this attribute
        self.file_dict: Dict[str, "ZipFileTreeNode"] = {}


def get_zip_file_tree(zf: zipfile.ZipFile):
    """用 pathlib 构建 ZIP 树形结构"""
    root = ZipFileTreeRoot()

    for info in zf.filelist:
        filename = _get_filename_str(info)
        if info.is_dir():
            filename = filename.rstrip("/")
            basename = os.path.basename(filename)
            dirname = os.path.dirname(filename)
            parent = root.find_dir(dirname, root)
            ZipFileTreeNode(info, basename, parent, root)
        else:
            dirname = os.path.dirname(filename)
            parent = root.find_dir(dirname, root)
            basename = os.path.basename(filename)
            ZipFileTreeNode(info, basename, parent, root)

    return root


if __name__ == '__main__':
    zip_dir(sys.argv[1], sys.argv[2])
