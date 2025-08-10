# encoding=utf-8
from xnote.plugin import TextLink

class LinkConfig:
    app_index = TextLink(text="应用", href="/system/index")
    develop_index = TextLink(text="开发", href="/plugin_list?category=develop")
