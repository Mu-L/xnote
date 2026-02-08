import zipfile
import web
import os

from typing import Optional, List
from xnote.core import xauth
from xutils import textutil, ziputil, fsutil
from . import fs_helper
from .fs_helper import FileItem
from .fs import FileSystemHandler

class ZipFileHandler(FileSystemHandler):
    
    def fix_zip_filename(self, filename: str):
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

    def read_zip_file(self, zip_path: str, inner_path: str):
        with zipfile.ZipFile(zip_path, "r") as zf:
            is_dir = False
            found: Optional[zipfile.ZipInfo] = None
            
            if inner_path == "":
                is_dir = True
            else:
                found = ziputil.find_file_in_zip(zf, inner_path)
                if found is None:
                    extra = f"class = ZipFileHandler, zip_path = {zip_path}, inner_path = {inner_path}"
                    yield self.not_readable(zip_path, extra=extra)
                    return
                is_dir = found.is_dir()
            
            if is_dir:
                yield self.read_zip_inner_dir(zf, inner_path, zip_path)
            else:
                assert found != None
                total_size = found.file_size
                web.header("Content-Length", total_size)
                self.handle_content_type(inner_path)
                expire_seconds = 3600 # 缓存1小时
                # 强制开启缓存
                web.header("Cache-Control", f"public, max-age={expire_seconds}")
                    
                chunk_size = 1024**2
                total_read = 0
                with zf.open(found.filename) as f:
                    while True:
                        chunk = f.read(chunk_size)
                        total_read += len(chunk)
                        # logging.debug("filename=%s, total_read=%s, total_size=%s", found.filename, total_read, total_size)
                        if not chunk:
                            break
                        yield chunk
                        
    def zip_info_to_file_item(self, zip_info: zipfile.ZipInfo, zip_path: str):
        fixed_name = self.fix_zip_filename(zip_info.filename)
        file_item = FileItem(fixed_name)
        file_item.size = fsutil.format_size(zip_info.file_size)
        if zip_info.is_dir():
            file_item.type = "dir"
        else:
            file_item.type = "file"
        encoded_path = textutil.encode_uri_component(fixed_name)
        zip_path_b64 = textutil.encode_base64(zip_path)
        file_item.customized_url = f"/fs/zip/{zip_path_b64}/{encoded_path}"
        fs_helper.handle_file_item(file_item)
        return file_item
    
    def read_zip_inner_dir(self, zf: zipfile.ZipFile, inner_path: str, zip_path: str):
        filelist: List[FileItem] = []
        if inner_path == "":
            # root
            for zip_info in zf.filelist:
                if ziputil.is_in_root_dir(zip_info):
                    file_item = self.zip_info_to_file_item(zip_info, zip_path)
                    filelist.append(file_item)
        else:
            for zip_info in zf.filelist:
                if ziputil.is_child_of(zip_info, inner_path):
                    file_item = self.zip_info_to_file_item(zip_info, zip_path)
                    filelist.append(file_item)
        
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
            item.customized_url = f"/fs/zip/{zip_path_b64}{abspath}/"
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