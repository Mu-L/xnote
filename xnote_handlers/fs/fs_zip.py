import zipfile
import web
import os
import logging

from typing import Optional, List
from xnote.core import xauth
from xutils import textutil, ziputil, fsutil
from . import fs_helper
from .fs_helper import FileItem
from .fs import FileSystemHandler

class ZipFileHandler(FileSystemHandler):

    def read_zip_file(self, zip_path: str, inner_path: str):
        inner_path = inner_path.rstrip("/")
        with zipfile.ZipFile(zip_path, "r") as zf:
            is_dir = False
            found: Optional[ziputil.ZipFileTreeNode] = None
            file_tree = ziputil.get_zip_file_tree(zf)

            file_tree.print_tree()
            
            if inner_path == "" or inner_path == "/":
                is_dir = True
                found = file_tree
            else:
                found = file_tree.file_dict.get(inner_path)
                if found is None:
                    extra = f"class = ZipFileHandler, zip_path = {zip_path}, inner_path = {inner_path}"
                    yield self.not_readable(zip_path, extra=extra)
                    return
                is_dir = found.is_dir
            if is_dir:
                yield self.read_zip_inner_dir(found, zip_path)
            else:
                assert found != None
                zip_info = found.zip_info
                assert zip_info != None
                total_size = zip_info.file_size
                web.header("Content-Length", total_size)
                self.handle_content_type(inner_path)
                expire_seconds = 3600 # 缓存1小时
                # 强制开启缓存
                web.header("Cache-Control", f"public, max-age={expire_seconds}")
                    
                chunk_size = 1024**2
                total_read = 0
                with zf.open(zip_info.filename) as f:
                    while True:
                        chunk = f.read(chunk_size)
                        total_read += len(chunk)
                        # logging.debug("filename=%s, total_read=%s, total_size=%s", zip_info.filename, total_read, total_size)
                        if not chunk:
                            break
                        yield chunk
                        
    def tree_node_to_file_item(self, tree_node: ziputil.ZipFileTreeNode, zip_path: str):
        file_item = FileItem(tree_node.name)
        if tree_node.is_dir:
            file_item.type = "dir"
            file_item.size = "-"
        else:
            assert tree_node.zip_info != None
            file_item.type = "file"
            file_item.size = fsutil.format_size(tree_node.zip_info.file_size)
        encoded_path = textutil.encode_uri_component(tree_node.path)
        zip_path_b64 = textutil.encode_base64(zip_path)
        file_item.customized_url = f"/fs/zip/{zip_path_b64}/{encoded_path}"
        fs_helper.handle_file_item(file_item)
        return file_item
    
    def read_zip_inner_dir(self, found: ziputil.ZipFileTreeNode, zip_path: str):
        inner_path = found.path
        filelist: List[FileItem] = []
        for tree_node in found.children:
            file_item = self.tree_node_to_file_item(tree_node, zip_path)
            filelist.append(file_item)
        
        def sort_key(node: ziputil.ZipFileTreeNode):
            if node.is_dir:
                return 0
            return 1
        
        fs_helper.sort_files(filelist)
    
        web.header("Content-Type", "text/html")
        path = os.path.join(zip_path, inner_path)
        fs_path_list = self.build_fs_path_list(zip_path, inner_path)
        return self.render_file_list(path, filelist, fs_path_list)
    
    def build_fs_path_list(self, zip_path: str, inner_path: str):
        zip_item = FileItem(path = zip_path)
        zip_path_b64 = textutil.encode_base64(zip_path)
        zip_item.customized_url = f"/fs/zip/{zip_path_b64}/"
        fs_helper.handle_file_item(zip_item)
        
        zip_parent = os.path.dirname(zip_path)
        result = fsutil.splitpath(zip_parent)
        for item in result:
            fs_helper.handle_file_item(item)
        
        result.append(zip_item)
                
        dirname = ""
        for path in inner_path.split("/"):
            if path == "":
                continue
            abspath = dirname + "/" + path
            item = FileItem(path = abspath)
            item.customized_url = f"/fs/zip/{zip_path_b64}{abspath}"
            fs_helper.handle_file_item(item)
            result.append(item)
            dirname = abspath
                
        return result

    @xauth.admin_required()
    def GET(self, path = ""):
        # 文件路径默认都进行urlencode
        # 如果存储结构不采用urlencode，那么这里也必须unquote回去
        path = self.resolve_fpath(path)
        parts = path.split("/", 1)
        inner_path = ""
        if len(parts) == 1:
            zip_path = parts[0]
        else:
            zip_path, inner_path = parts
        zip_path = textutil.decode_base64(zip_path)
        return self.read_zip_file(zip_path, inner_path)
    
xurls = (
    r"/fs/zip/(.*)", ZipFileHandler,
)