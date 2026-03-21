# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2017
# @modified 2018/09/22 01:17:06

import re
import html

from typing import List


class RawHtml:
    def __init__(self, html: str):
        self.html = html

def element(tag, text, clazz, attrs = None):
    """
        >>> element('span', '123', 'test')
        "<span class='test'>123</span>"
    """
    attrs_text = ''
    if attrs is not None:
        for attr in attrs:
            value = attrs[attr]
            attrs_text += ' %s=%s' % (attr, value)
    return "<%s class='%s' %s>%s</%s>" % (tag, clazz, attrs_text, text, tag)

def span(text, clazz = 'xnote-span'):
    return element("span", text, clazz)


def pre(text, clazz = 'xnote-pre'):
    """
        >>> pre('hello')
        "<pre class='xnote-pre'>hello</pre>"
    """
    return element("pre", text, clazz)

def div(text, clazz = 'xnote-div'):
    return element("div", text, clazz)

def link(name, link = None, clazz = "xnote-link"):
    if link is None:
        link = name
    return "<a class='%s' href='%s'>%s</a>" % (clazz, link, name)

def button(name, onclick=None, clazz='xnote-btn'):
    return element('button', name, clazz, dict(onclick=onclick))


def highlight(content: str, words: List[str], css_class="highlight-word") -> str:
    """对content中的关键字进行高亮标记
    
    :param content: 输入的文本
    :param words: 关键字列表
    :return: html片段
    """
    
    # 过滤空关键字
    words = [word for word in words if word]
    if not words:
        return html.escape(content)
    
    # 对content进行HTML转义
    content_escaped = html.escape(content)
    
    # 对每个关键字进行HTML转义并生成正则表达式
    for word in words:
        word_escaped = html.escape(word)
        pattern = re.compile(re.escape(word_escaped), re.IGNORECASE)
        # 在转义后的content上进行匹配和替换
        content_escaped = pattern.sub(lambda m: f"<span class='{css_class}'>{m.group()}</span>", content_escaped)
    
    return content_escaped


