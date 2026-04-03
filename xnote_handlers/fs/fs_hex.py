# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2019-01-10 00:21:16
@LastEditors  : xupingmao
@LastEditTime : 2024-06-16 11:56:55
@FilePath     : /xnote/handlers/fs/fs_hex.py
@Description  : 二进制查看工具
"""

import os
import math
import xutils
from xutils import textutil
from xutils import Storage
from xnote.core.xtemplate import BasePlugin

HTML = """
<!-- Html -->
<style>
    .hex-viewer {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 20px;
        display: flex;
        flex-direction: row;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: auto;
        max-height: 600px;
    }

    .hex-col-index {
        width: 80px;
        flex-shrink: 0;
        background-color: #e8e8e8;
        border-right: 1px solid #ccc;
        padding: 8px 4px;
        text-align: right;
        color: #666;
        user-select: none;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .hex-col-hex {
        width: 400px;
        flex-shrink: 0;
        padding: 8px 4px;
        border-right: 1px solid #ccc;
        cursor: text;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .hex-col-ascii {
        width: 160px;
        flex-shrink: 0;
        padding: 8px 4px;
        color: #333;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    /* 确保内容区域填充整个列 */
    .hex-col-index > div,
    .hex-col-hex > div,
    .hex-col-ascii > div {
        flex: 1;
    }

    .hex-row {
        height: 20px;
        white-space: nowrap;
    }

    .hex-char {
        display: inline-block;
        width: 18px;
        text-align: center;
        user-select: text;
    }

    .hex-char.selected {
        background-color: #007acc;
        color: white;
    }

    .hex-char.highlighted {
        background-color: #007acc;
        color: white;
    }

    .hex-char::selection {
        background-color: #007acc;
        color: white;
    }

    .hex-char-space {
        display: inline-block;
        width: 6px;
    }

    .ascii-char {
        display: inline-block;
        width: 10px;
        text-align: center;
        user-select: none;
    }

    .ascii-char.highlighted {
        background-color: #007acc;
        color: white;
    }

    .ascii-char::selection {
        background-color: #007acc;
        color: white;
    }

    .index-char {
        display: inline-block;
        user-select: none;
    }

    {% if embed == "true" %}
    body {
        background-color: transparent;
    }
    .card.embed {
        padding: 0px;
    }
    .x-body {
        margin-top: 0px;
    }
    {% end %}
</style>

{% init plain_text = "" %}
{% if embed != "true"  %}
    <div class="card embed">
        <div class="card-title btn-line-height">
            <span>二进制查看</span>
            
            <div class="float-right">
                <a class="btn btn-default" href="{{_server_home}}/code/edit?path={{path}}&embed={{embed}}">编辑本文</a>
                {% include common/button/back_button.html %}
            </div>
        </div>
    </div>
{% end %}

<div class="card">
    {% if embed == "false" %}
        {% include mod_fs_path.html %}
    {% else %}
        <div class="row bottom-offset-2">
            <a class="btn btn-default" href="{{_server_home}}/code/edit?path={{path}}&embed={{embed}}">编辑本文</a>
        </div>
    {% end %}

    {% if error != "" %}
        <div class="error">{{error}}</div>
    {% end %}

    <div class="hex-viewer" id="hexViewer">
        <div class="hex-col-index" id="hexIndex">{% raw lineno_html %}</div>
        <div class="hex-col-hex" id="hexContent">{% raw hex_html %}</div>
        <div class="hex-col-ascii" id="hexAscii">{% raw ascii_html %}</div>
    </div>
</div>

<script>
(function() {
    var hexViewer = document.getElementById('hexViewer');
    var hexContent = document.getElementById('hexContent');
    var hexAscii = document.getElementById('hexAscii');
    
    // 获取所有hex字符和ascii字符
    var hexChars = hexContent.querySelectorAll('.hex-char');
    var asciiChars = hexAscii.querySelectorAll('.ascii-char');
    
    // 清除所有高亮
    function clearHighlight() {
        // 清除高亮类
        hexChars.forEach(function(char) {
            char.classList.remove('highlighted');
        });
        asciiChars.forEach(function(char) {
            char.classList.remove('highlighted');
        });
        
        // 清除浏览器默认选择
        if (window.getSelection) {
            window.getSelection().removeAllRanges();
        } else if (document.selection) {
            document.selection.empty();
        }
    }
    
    // 高亮指定范围的字符
    function highlightRange(startIndex, endIndex) {
        clearHighlight();
        for (var i = startIndex; i <= endIndex && i < hexChars.length; i++) {
            if (hexChars[i]) {
                hexChars[i].classList.add('highlighted');
            }
            if (asciiChars[i]) {
                asciiChars[i].classList.add('highlighted');
            }
        }
    }
    
    // 获取字符的索引
    function getCharIndex(charElement) {
        var index = charElement.getAttribute('data-index');
        return index !== null ? parseInt(index, 10) : -1;
    }
    
    // 监听鼠标选择事件
    var isSelecting = false;
    var startIndex = -1;
    
    hexContent.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('hex-char')) {
            isSelecting = true;
            startIndex = getCharIndex(e.target);
            clearHighlight();
            e.target.classList.add('highlighted');
            var asciiIndex = getCharIndex(e.target);
            if (asciiIndex >= 0 && asciiChars[asciiIndex]) {
                asciiChars[asciiIndex].classList.add('highlighted');
            }
        }
    });
    
    // 监听ASCII列的鼠标选择事件
    hexAscii.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('ascii-char')) {
            isSelecting = true;
            startIndex = getCharIndex(e.target);
            clearHighlight();
            e.target.classList.add('highlighted');
            var hexIndex = getCharIndex(e.target);
            if (hexIndex >= 0 && hexChars[hexIndex]) {
                hexChars[hexIndex].classList.add('highlighted');
            }
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isSelecting) return;
        
        var target = e.target;
        if (target.classList.contains('hex-char') || target.classList.contains('ascii-char')) {
            var currentIndex = getCharIndex(target);
            if (currentIndex >= 0 && startIndex >= 0) {
                var minIndex = Math.min(startIndex, currentIndex);
                var maxIndex = Math.max(startIndex, currentIndex);
                highlightRange(minIndex, maxIndex);
            }
        }
    });
    
    document.addEventListener('mouseup', function() {
        isSelecting = false;
    });
    
    // 监听选择变化（用于键盘选择等情况）
    document.addEventListener('selectionchange', function() {
        var selection = window.getSelection();
        if (selection.rangeCount > 0) {
            // 检查是否在hex列
            if (hexContent.contains(selection.anchorNode)) {
                var range = selection.getRangeAt(0);
                var startContainer = range.startContainer;
                var endContainer = range.endContainer;
                
                // 找到包含的hex-char元素
                var startChar = startContainer.parentElement;
                var endChar = endContainer.parentElement;
                
                if (startChar && startChar.classList.contains('hex-char') &&
                    endChar && endChar.classList.contains('hex-char')) {
                    var startIdx = getCharIndex(startChar);
                    var endIdx = getCharIndex(endChar);
                    if (startIdx >= 0 && endIdx >= 0) {
                        highlightRange(Math.min(startIdx, endIdx), Math.max(startIdx, endIdx));
                    }
                }
            } 
            // 检查是否在ASCII列
            else if (hexAscii.contains(selection.anchorNode)) {
                var range = selection.getRangeAt(0);
                var startContainer = range.startContainer;
                var endContainer = range.endContainer;
                
                // 找到包含的ascii-char元素
                var startChar = startContainer.parentElement;
                var endChar = endContainer.parentElement;
                
                if (startChar && startChar.classList.contains('ascii-char') &&
                    endChar && endChar.classList.contains('ascii-char')) {
                    var startIdx = getCharIndex(startChar);
                    var endIdx = getCharIndex(endChar);
                    if (startIdx >= 0 && endIdx >= 0) {
                        highlightRange(Math.min(startIdx, endIdx), Math.max(startIdx, endIdx));
                    }
                }
            }
        }
    });
})();
</script>
"""

from typing import List, Union, Optional, Dict

HEX_DICT: Dict[int, str] = {}
for i in range(256):
    HEX_DICT[i] = '%02x' % i


def bytes_hex(bytes_data: bytes) -> List[str]:
    """将字节转换为hex字符串列表"""
    out = []
    for b in bytes_data:
        out.append(HEX_DICT[b])
    return out


def bytes_chars(bytes_data: bytes) -> List[str]:
    """将字节转换为可打印字符列表"""
    out = []
    for b in bytes_data:
        c = chr(b)
        if c.isprintable() and b >= 32:
            out.append(c)
        else:
            out.append('.')
    return out


class Main(BasePlugin):

    show_title = False
    # 提示内容
    description = ""
    # 是否需要管理员权限
    require_admin = True
    category = 'dir'
    editable = False

    def _generate_lineno_html(self, line_fmt: str, offset: int, row: int) -> str:
        """生成行索引的HTML"""
        return '<div class="hex-row"><span class="index-char">{}</span></div>'.format(
            line_fmt % (offset + row * 16)
        )

    def _generate_hex_html(self, bytes_data: bytes, global_char_index: int) -> str:
        """生成hex列的HTML"""
        hex_row_html = '<div class="hex-row">'
        hex_chars: List[str] = bytes_hex(bytes_data)
        step = 16
        
        for i, hex_char in enumerate(hex_chars):
            hex_row_html += '<span class="hex-char" data-index="{}">{}</span>'.format(
                global_char_index + i, hex_char
            )
            if i < len(hex_chars) - 1:
                hex_row_html += '<span class="hex-char-space"></span>'
        
        for i in range(len(hex_chars), step):
            hex_row_html += '<span class="hex-char" data-index="{}">&nbsp;&nbsp;</span>'.format(
                global_char_index + i
            )
            if i < step - 1:
                hex_row_html += '<span class="hex-char-space"></span>'
        
        hex_row_html += '</div>'
        return hex_row_html

    def _generate_ascii_html(self, bytes_data: bytes, global_char_index: int) -> str:
        """生成ASCII列的HTML"""
        ascii_row_html = '<div class="hex-row">'
        ascii_chars: List[str] = bytes_chars(bytes_data)
        step = 16
        
        for i, ascii_char in enumerate(ascii_chars):
            if ascii_char == '<':
                ascii_char = '&lt;'
            elif ascii_char == '>':
                ascii_char = '&gt;'
            elif ascii_char == '&':
                ascii_char = '&amp;'
            elif ascii_char == ' ':
                ascii_char = '&nbsp;'
            ascii_row_html += '<span class="ascii-char" data-index="{}">{}</span>'.format(
                global_char_index + i, ascii_char
            )
        
        for i in range(len(ascii_chars), step):
            ascii_row_html += '<span class="ascii-char" data-index="{}">&nbsp;</span>'.format(
                global_char_index + i
            )
        
        ascii_row_html += '</div>'
        return ascii_row_html

    def _read_file_and_generate_html(self, path: str, offset: int, pagesize: int) -> tuple:
        """读取文件并生成HTML"""
        lineno_html: str = ""
        hex_html: str = ""
        ascii_html: str = ""
        error: str = ""
        global_char_index: int = 0
        step = 16
        
        try:
            with open(path, 'rb') as fp:
                fp.seek(offset)
                row: int = 0
                while row * step < pagesize:
                    bytes_data: bytes = fp.read(step)
                    if len(bytes_data) == 0:
                        break
                    
                    lineno_html += self._generate_lineno_html("%05x", offset, row)
                    hex_html += self._generate_hex_html(bytes_data, global_char_index)
                    ascii_html += self._generate_ascii_html(bytes_data, global_char_index)
                    
                    global_char_index += len(bytes_data)
                    row += 1
        except Exception as e:
            xutils.print_exc()
            error = str(e)
        
        return lineno_html, hex_html, ascii_html, error

    def handle(self, input: str = "") -> Optional[str]:
        """处理请求"""
        self.rows = 0
        self.show_pagenation = True
        self.page_max = 0

        pagesize = 16 * 30

        path = xutils.get_argument_str("path", "")
        page = xutils.get_argument_int("page", 1)
        is_b64 = xutils.get_argument_bool("b64")
        if is_b64:
            path = textutil.decode_base64(path)
        else:
            path = xutils.get_real_path(path)

        offset = max(page-1, 0) * pagesize
        embed = xutils.get_argument_str("embed", "false")

        self.page_url = "?path={path}&embed={embed}&page=".format(path=path, embed=embed)
        
        if path == "":
            return

        if not os.path.isfile(path):
            return "`%s` IS NOT A FILE!" % path

        filesize = xutils.get_file_size(path, format=False)
        assert isinstance(filesize, int)
        self.page_max = math.ceil(filesize / pagesize)

        lineno_html, hex_html, ascii_html, error = self._read_file_and_generate_html(path, offset, pagesize)

        kw = Storage()
        kw.path = path
        kw.lineno_html = lineno_html
        kw.hex_html = hex_html
        kw.ascii_html = ascii_html
        kw.embed = embed
        kw.error = error

        if embed == "true":
            self.show_nav = False

        self.writetemplate(HTML, **kw)

    def on_init(self, context: Optional[dict] = None) -> None:
        # 插件初始化操作
        pass

    def command(self) -> None:
        pass


xurls = (
    r"/fs_hex", Main
)
