# -*- coding:utf-8 -*-
"""
@Author       : xupingmao
@email        : 578749341@qq.com
@Date         : 2021-01-10 14:36:09
@LastEditors  : xupingmao
@LastEditTime : 2024-08-24 22:59:25
@FilePath     : /xnote/xutils/text_parser.py
@Description  : 描述
"""

"""标记文本解析

类
- 文本解析器的基类      TextParserBase(text:str)
- 文本解析器           TextParser

函数
- HTML转义            escape_html(text:str)

"""
import os
import typing
from xutils.base import Storage
from urllib.parse import quote, unquote


class TextParserConfig:
    img_ext_set = set([".png", ".jpg", ".gif"])

def invoke_deco(prefix = ""):
    """日志装饰器"""
    def deco(func):
        def handle(*args, **kw):
            try:
                result = func(*args, **kw)
                print(prefix, args, kw, result)
                return result
            except Exception as e:
                print("exception occurs", prefix, args, kw)
                raise e
        return handle
    return deco

def is_img_file(filename):
    """根据文件后缀判断是否是图片"""
    from xutils import fsutil
    realname = fsutil.decode_name(filename)
    name, ext = os.path.splitext(realname)
    return ext.lower() in TextParserConfig.img_ext_set

def set_img_file_ext(img_set):
    TextParserConfig.img_ext_set = img_set

def escape_html(text: str, quote=True):
    # 必须先处理&
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    if quote:
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#39;")
        text = text.replace(" ", "&nbsp;")
        text = text.replace("\n", "<br/>")
    return text


class BaseTextParser(object):

    """文本解析工具, 有这些规则
    - 下标默认从0开始(也就是默认读取第一个字符)
    - read_till_XXX 指从当前字符读取到目标字符，读完后下标{i}位于目标字符之后的一个字符
    - read_before_XXX 从当前字符读取到目标字符之前的一个字符，读完后下标{i}位于目标字符


    index   value    Description
    -------------------------------
   -1       None  
    0       i        -> 开始的下标
    1       n        
    2       p        -> current 当前字符 (self.i = 2)
    3       u        -> next    下一个字符
    4       t
    5       None

    """


    # 调试的开关
    debug_flag = False
    # 空白字符
    blank_chars = set([" ", "\t", "\n", "\r"])

    def init(self, text: str):
        text = text.replace("\r", "")
        text = text.replace(u'\xad', '\n')

        self.text = text
        self.str_token = ""
        self.tokens: typing.List[TextToken] = []
        # 当前读取的字符下标，默认初始化为第一个字符
        self.i = 0
        self.length = len(text)
        self.max_index = self.length - 1

        # 循环分析
        self.profile_dict = dict()

    @property
    def pos(self):
        return self.i
    
    def escape(self, text):
        return escape_html(text)

    def current(self):
        """当前的字符，如果越界了，返回空字符串"""
        if self.i < self.length:
            return self.text[self.i]
        return ""
    
    def has_next(self):
        return self.i < self.length
    
    def read(self, count=1):
        """往后读取 {count} 个字符, 如果读取不到字符, 返回空字符串, 始终会修改当前位置索引"""
        assert count > 0
        pos = self.i
        newpos = self.i + count
        self.i = newpos
        return self.text[pos+1:newpos+1]

    def read_next(self):
        """往后读取一个字符，返回读取的字符，如果已经读完了，返回空字符串，改变索引下标"""
        return self.read(1)

    def peek(self, pos=1):
        """读取后面的字符，如果没有返回空字符串，不改变当前索引下标"""
        newpos = self.i + pos
        if 0 <= newpos <= self.max_index:
            return self.text[newpos]
        return ""
    
    lookahead = peek

    def get(self, index=0):
        if index < self.max_index:
            return self.text[index]
        return ""

    def seek(self, index: int):
        if index < 0:
            raise Exception(f"invalid index={index}")
        self.i = index

    set_index = seek

    def startswith(self, target: str):
        """当前字符是否以{target}开头"""
        length = len(target)
        return self.text[self.i:self.i+length] == target

    def find(self, target: str):
        """
        以{self.i}作为开始下标，寻找目标字符串

        :param target: 目标字符 
        :return: 目标字符串的索引下标，如果找不到返回-1
        """
        return self.text.find(target, self.i)

    def find_blank(self):
        """找到一个空白字符
        
        :return: 第一个空白字符的索引，如果找不到返回-1
        """
        i = self.i
        for i in range(self.i, self.length):
            c = self.text[i]
            if c in self.blank_chars:
                return i

        return -1

    def str_token_append(self, c: str):
        """追加字符到str_token"""
        self.str_token += c

    def save_str_token(self):
        if self.str_token != "":
            token_str = self.str_token
            token = TextToken(value=token_str)
            self.tokens.append(token)
        self.str_token = ""

    def read_until_blank(self):
        """从当前字符开始，找到空白字符为止，返回内容不包含空白字符,读取后{i}位于第一个空白字符
        读取完成后 current() 返回空白字符或者空字符串
        """
        end = self.find_blank()
        if end < 0:
            found = self.text[self.i:]
            # 全部读完，当前索引处于有效范围外
            self.i = self.length
        else:
            found = self.text[self.i:end]
            # 位于第一个空白字符
            self.i = end
        return found

    def read_until_index(self, index: int):
        """包含目标索引，读取后{i}=index+1"""
        start_index = self.i
        self.i = min(self.length, index+1)
        return self.text[start_index:self.i]

    def read_before_index(self, index: int):
        """不包含目标索引，读取后{i}=index"""
        start_index = self.i
        self.i = min(self.length, index)
        return self.text[start_index:self.i]

    def read_number(self):
        """读取后{i}位于第一个非数字位"""
        i = 0
        for i in range(self.i, self.length):
            c = self.text[i]
            if not c.isdigit():
                token = self.text[self.i:i]
                # 当前处于数字后的第一个字符
                self.i = i
                return token
        token = self.text[self.i:]
        self.i = i + 1
        return token

    def read_rest(self):
        return self.read_until_index(self.max_index)

    def read_until_target(self, target: str):
        """返回值包含target，索引{i}移动到target之后"""
        end = self.text.find(target, self.i+1)
        if end < 0:
            return ""
        else:
            key = self.text[self.i:end+len(target)]
            # 包含 target
            self.i = end + len(target)
        return key
    
    def read_until_any_target(self, target_list: typing.Sequence):
        """返回值包含target，索引{i}移动到target之后"""
        pos_list = []
        pos_target_map = {} # position -> target
        for target in target_list:
            end = self.text.find(target, self.i+1)
            if end >= 0:
                pos_list.append(end)
                pos_target_map[end] = target
        
        if len(pos_list) > 0:
            end = min(pos_list) # type: int
            target = pos_target_map[end]
            key = self.text[self.i:end+len(target)]
            # 包含 target
            self.i = end + len(target)
            return key
        # 无匹配项
        return ""
    
    def append_token(self, token):
        self.save_str_token()
        self.tokens.append(TextToken(token))

    def profile(self, name):
        if not self.debug_flag:
            return

        visit_cnt = self.profile_dict.get(name, 0) + 1
        if visit_cnt >= 1000:
            print("there maybe dead loops in [%s]" % name)
        self.profile_dict[name] = visit_cnt

    def parse(self, text: str):
        raise Exception("parse() must be implemented by child class")
    
    def get_text_tokens(self, tokens: typing.List["TextToken"]):
        result: typing.List[str] = []
        for token in tokens:
            result.append(token.get_html())
        return result
    
    def is_blank(self):
        return self.current() in self.blank_chars
    
    def is_blank_char(self, char: str):
        return char in self.blank_chars
    
    def is_eof(self):
        return self.i > self.max_index
    
    def skip_blank(self):
        while self.is_blank():
            self.read(1)

TextParserBase = BaseTextParser

class TokenType:
    text = "text"
    link = "link"
    topic = "topic"
    heading = "heading"
    strong = "strong"
    phone_number = "phone_number"
    search = "search"
    img = "img"
    img_list = "img_list"
    code_block = "code_block"

class TextToken(Storage):
    def __init__(self, value=""):
        super().__init__()
        self.type = TokenType.text
        self.value = value
        self.html = ""

    def get_html(self):
        if self.html != "":
            return self.html
        return escape_html(self.value)
    
    def __eq__(self, value: "TextToken") -> bool:
        return self.type == value.type and self.value == value.value
    
    @property
    def is_topic(self):
        return self.type == TokenType.topic
    
    @property
    def is_heading(self):
        return self.type == TokenType.heading

class TopicToken(TextToken):
    def __init__(self, value=""):
        super().__init__(value=value)
        self.type = TokenType.topic
        self.value = value

    def get_html(self):
        if self.html != "":
            return self.html
        quoted_key = quote(self.value)
        value = escape_html(self.value)
        return f"<a class=\"link hashtag\" href=\"/message?category=message&key={quoted_key}\">{value}</a>"

class HeadingToken(TextToken):
    def __init__(self, value="", level=1, title=""):
        super().__init__(value=value)
        self.type = TokenType.heading
        self.value = value
        self.level = level
        self.title = title

    def get_html(self):
        if self.html != "":
            return self.html
        title = escape_html(self.title)
        tag = f"h{self.level}"
        return f"""<{tag} class="block-title">{title}</{tag}>"""


class SearchToken(TopicToken):
    def __init__(self, value=""):
        super().__init__(value=value)
        self.type = TokenType.search
        self.value = value

class StrongToken(TextToken):
    def __init__(self, value="", tag = "**"):
        super().__init__(value=value)
        self.type = TokenType.strong
        self.value = value
        self.tag = tag
        
    def get_html(self):
        value = self.value.strip("*")
        value = escape_html(value)
        level = len(self.tag)
        return f'<span class="msg-strong level-{level}">{value}</span>'

class CodeBlockToken(TextToken):
    def __init__(self, value="", language="", code=""):
        super().__init__(value=value)
        self.type = TokenType.code_block
        self.value = value
        self.language = language
        self.code = code
        
    def get_html(self):
        if self.html != "":
            return self.html
        # 只转义HTML特殊字符，不转换换行符
        code = escape_html(self.code, quote=False)
        return f'<pre class="code-block" data-lang="{self.language}"><code>{code}</code></pre>'

class LinkToken(TextToken):
    def __init__(self, value="", href="", name = ""):
        super().__init__(value=value)
        self.type = TokenType.link
        self.value = value
        self.href = href
        if name == "":
            self.name = value
        else:
            self.name = name
    
    def get_html(self):
        return f'<a target="_blank" href="{self.href}">{self.name}</a>'

class ImageToken(TextToken):
    def __init__(self, value="", href="", has_multi=False):
        super().__init__(value=value)
        self.type = TokenType.img
        self.value = value
        self.href = href
        self.has_multi = has_multi

    def get_html(self):
        if self.html != "":
            return self.html
        href = self.href
        thumb_href = f"{href}?mode=thumbnail_v2"
        if self.has_multi:
            box_class = "msg-img-box multi"
        else:
            box_class = "msg-img-box"
        return f'<div class="{box_class}"><img class="msg-img x-photo" alt="{href}" src="{thumb_href}" data-src="{href}"></div>'

    def __eq__(self, value: "ImageToken") -> bool:
        return self.type == value.type and self.value == value.value and self.href == value.href


class ImageListToken(TextToken):
    def __init__(self, tokens: typing.List[ImageToken]):
        self.type = TokenType.img_list
        self.tokens = tokens
        values = [x.value for x in tokens]
        self.value = "".join(values)
    
    def get_html(self):
        html = '<div class="row">'
        for item in self.tokens:
            item.has_multi = True
            html += item.get_html()
        html += '</div>'
        return html


class TextParser(BaseTextParser):

    # 是否标记单书名号<书籍名>
    mark_book_single_flag = False

    # 是否标记数字
    mark_number_flag = False

    # 是否记录关键字，关键字包括话题、书籍、@值等等
    record_keyword_flag = True
    # 关键字转小写
    keyword_to_lower = True

    # 话题的长度限制
    topic_len_limit = 100

    def init_ext(self, text):
        self.keywords = set()
        self.headings = set()

    def record_keyword(self, keyword:str):
        if self.keyword_to_lower:
            keyword = keyword.lower()
        self.keywords.add(keyword)

    def record_heading(self, heading:str):
        self.headings.add(heading)

    def build_search_link(self, keyword):
        return SearchToken(keyword)

    def translate_topic(self, key):
        return TopicToken(value=key)

    def mark_hashtag(self):
        """话题转为搜索关键字的时候去掉前后的#符号"""
        self.profile("mark_topic")
        start_index = self.i
        key0 = None

        for i in range(self.i+1, self.length):
            c = self.text[i]
            if self.is_blank_char(c):
                # 话题终止
                key0 = self.text[start_index:i]
                self.i = i
                break
            
            if c == '#':
                # '#'字符结束,包含尾部的'#'字符
                key0 = self.text[start_index: i + 1]
                self.i = i + 1
                break
            
            if c == '\n':
                # 换行终止
                key0 = self.text[start_index: i]
                self.i = i
                break

        if key0 is None:
            # 读到文本结束了
            key0 = self.read_rest()

    
        if key0 == "#" or key0 == "##":
            # 连续的##字符, 无效的话题
            self.str_token_append(key0)
            return

        if len(key0) > self.topic_len_limit:
            # 超过限制，不认为是话题
            self.str_token_append('#')
            self.i = start_index + 1
            return
        # 记录关键字
        self.record_keyword(key0)
        # 处理转换逻辑
        token = self.translate_topic(key0)
        self.tokens.append(token)

    def mark_heading(self):
        # 当前处于#字符
        level = 0
        start = self.pos
        while self.current() == "#":
            level += 1
            self.read()
        
        self.skip_blank()
        heading_text = self.read_until_target("\n")
        if heading_text == "":
            # 最后一行没有换行符
            heading_text = self.read_rest()
        heading_text = heading_text.strip()
        raw_value = self.text[start:self.pos]
        self.record_heading(heading_text)
        self.tokens.append(HeadingToken(value=raw_value, level=level, title=heading_text))

    def mark_http(self):
        self.profile("mark_http")
        link  = self.read_until_blank()
        token = LinkToken(value=link, href=link)
        self.tokens.append(token)

    def mark_https(self):
        return self.mark_http()

    def mark_book(self):
        return self.mark_tag_single("》")

    def mark_at(self):
        self.profile("mark_at")
        
        word  = self.read_until_blank()
        token = self.build_search_link(word)
        self.tokens.append(token)

        # 记录关键字
        self.record_keyword(word)
    
    def mark_strong(self, tag="**"):
        # tag_len = len(tag)
        self.i += len(tag)
        
        key = self.read_until_any_target((tag,"\n"))
        if key == "":
            # 无匹配的
            self.tokens.append(TextToken(tag))
            return
        
        key = tag + key
        if key.endswith("\n"):
            # 不是完整的tag
            self.tokens.append(TextToken(key))
        else:
            # key = key[0:len(key)-tag_len]
            token = StrongToken(key, tag=tag)
            self.tokens.append(token)

    def mark_book_single(self):
        return self.mark_tag_single(">")

    def mark_number(self):
        self.profile("mark_number")
        number = self.read_number()
        token  = self.build_search_link(number)
        self.tokens.append(token)
        return token

    def mark_tag_single(self, end_char, record_keyword=True, build_html_tag_func=None, exclude_tag=False):
        self.profile("mark_tag_single")
        key = self.read_until_target(end_char)
        if key == "":
            self.str_token_append(self.text[self.i])
            # self.tokens.append(self.text[self.i])
            self.i += 1
            return

        if exclude_tag:
            key = key[1:-1]

        token = self.build_search_link(key)
        self.tokens.append(token)

        # 记录关键字
        if record_keyword:
            self.record_keyword(key)
    
    def handle_img_list(self, first_img_value="", href=""):
        restore_index = self.i
        tmp_tokens = [] # type: list[ImageToken]
        tmp_tokens.append(ImageToken(value=first_img_value, href=href))

        while True:
            restore_index = self.i

            self.skip_blank()

            if self.startswith("file://"):
                href = self.read_until_blank()
                href = href[7:]
                if not is_img_file(href):
                    self.i = restore_index
                    break
                else:
                    # img file
                    value = self.text[restore_index:self.i]
                    tmp_tokens.append(ImageToken(value=value, href=href))
            else:
                self.i = restore_index
                break
                
        if len(tmp_tokens) > 1:
            self.tokens.append(ImageListToken(tmp_tokens))
        else:
            self.tokens += tmp_tokens

    def mark_file(self):
        from xutils import fsutil
        self.profile("mark_file")
        value = self.read_until_blank()
        href = value[7:]
        if is_img_file(href):
            self.handle_img_list(value, href)
        else:
            name = href[href.rfind("/")+1:]
            # 尝试urldecode名称
            name = fsutil.decode_name(name)
            # token = '<a href="%s">%s</a>' % (href, name)
            token = LinkToken(value=value, href=href, name = name)
            self.tokens.append(token)

    def _get_strong_start(self):
        start = self.pos
        size = 0
        for pos in range(start, self.length):
            c = self.text[pos]
            if c != "*":
                break
            size += 1

        return self.text[start: start + size]

    def mark_code_block(self, code_block_start):
        start_pos = self.pos
        # 读取代码块开始标记
        self.read(len(code_block_start))  # 跳过剩余的反引号
        
        # 读取语言标签（如果有）
        language = ""
        while self.current() not in ("\n", ""):
            language += self.current()
            self.read(1)
        language = language.strip()
        
        if self.current() == "\n":
            self.read(1)
        
        # 读取代码内容直到遇到与开始标记相同的结束标记
        code_content = ""
        while True:
            # 检查是否到达文件末尾
            if not self.has_next():
                break
            
            # 检查是否是结束标记
            if self.startswith(code_block_start):
                if self.get(self.pos-1) == "\n":
                    # 之前的空白行不在代码块里面
                    code_content = code_content[:-1]
                    
                # 处理结束标记
                self.read(len(code_block_start))  # 跳过结束标记
                # 处理结束标记后面的换行符
                if self.current() == "\n":
                    self.read(1)
                break
            
            # 读取一个字符
            c = self.current()
            code_content += c
            self.read(1)
        
        end_pos = self.pos
        raw_value = self.text[start_pos:end_pos]
        # 创建代码块token
        token = CodeBlockToken(value=raw_value, language=language, code=code_content)
        self.tokens.append(token)

    def _get_code_block_start(self):
        """获取代码块的开始标记，返回连续的反引号字符串"""
        start = self.pos
        size = 0
        for pos in range(start, self.length):
            c = self.text[pos]
            if c != '`':
                break
            size += 1

        if size >= 3:
            return self.text[start: start + size]
        return ""

    def _next_token(self):
        c = self.current()
        if c == "":
            return
        
        prev_char = self.peek(-1)
        next_char = self.peek()

        if prev_char in ("\n", "") and c == '#' and (next_char in (" ", "#")) :
            self.save_str_token()
            self.mark_heading()
            return
        
        if c == '#':
            self.save_str_token()
            self.mark_hashtag()
            return
        
        if c == '《':
            self.save_str_token()
            self.mark_book()
            return
        
        if c == '@':
            self.save_str_token()
            self.mark_at()
            return
        
        # 检查代码块
        code_block_start = self._get_code_block_start()
        if code_block_start:
            self.save_str_token()
            self.mark_code_block(code_block_start)
            return
        
        tag = self._get_strong_start()
        if len(tag) >= 2:
            self.save_str_token()
            self.mark_strong(tag)
            return
        
        if self.mark_book_single_flag and c == '<':
            self.save_str_token()
            self.mark_book_single()
            return
        
        if self.mark_number_flag and c.isdigit():
            self.save_str_token()
            self.mark_number()
            return
        
        if self.startswith("http://"):
            self.save_str_token()
            self.mark_http()
            return
        
        if self.startswith("https://"):
            self.save_str_token()
            self.mark_https()
            return
        
        if self.startswith("file://"):
            self.save_str_token()
            self.mark_file()
            return
        
        if c == '\n':
            self.str_token_append(c)
            self.save_str_token()
            self.read_next()
            return
        
        # 未命中规则，保存并且往下读取一个字符
        self.str_token_append(c)
        self.read_next()

    def parse_to_tokens(self, text: str):
        self.init(text)
        self.init_ext(text)

        while self.has_next():
            self._next_token()
            # 前面都读取了一个字符，这里不需要再读取

        self.save_str_token()
        return self.tokens
    
    def parse(self, text=""):
        # 兼容原来的 parse 方法
        tokens = self.parse_to_tokens(text=text)
        return self.get_text_tokens(tokens)
    
    def render_html(self, text: str):
        tokens = self.parse_to_tokens(text)
        html_list = self.get_text_tokens(tokens)
        return "".join(html_list)
