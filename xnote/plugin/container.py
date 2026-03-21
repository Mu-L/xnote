from xnote.plugin.base import BaseComponent, BaseContainer
from xnote.plugin.component import TextSpan, EditFormButton, ConfirmButton, TextLink
from xnote.core import xtemplate
from typing import Optional

class ActionBar(BaseContainer):
    """表格动作栏"""
    def __init__(self, css_class=""):
        super().__init__(css_class=f"action-bar {css_class}")
        self.right_box = BaseContainer("float-right")
        self.add(self.right_box)

    def is_empty(self):
        return len(self.right_box.children) == 0 and len(self.children) == 1
    
    @property
    def visible(self):
        return not self.is_empty()

    def _add(self, item: BaseComponent, float_right=False):
        if float_right:
            self.right_box.add(item)
        else:
            self.add(item)

    def add_span(self, text="", css_class="", float_right=False, id=""):
        span = TextSpan(text=text, css_class=css_class, id=id)
        self._add(span, float_right)

    def add_edit_button(self, text="", url="", css_class="", float_right=False):
        btn = EditFormButton(text = text, url = url, css_class=css_class)
        self._add(btn, float_right)

    def add_confirm_button(self, text="", url="", message="", css_class="", method="GET", reload_url="", float_right=False):
        btn = ConfirmButton(text=text, url=url, message=message, method=method, reload_url=reload_url, css_class=css_class)
        self._add(btn, float_right)

    def add_link(self, text = "", href="", css_class="", float_right=False):
        link = TextLink(text=text, href=href, css_class=css_class)
        self._add(link, float_right)
    

class Card(BaseContainer):
    """卡片容器，一个卡片可以包含多个行"""
    def __init__(self, css_class="") -> None:
        super().__init__(css_class="card " + css_class)


class CardRow(BaseContainer):
    """行容器"""
    def __init__(self, css_class="") -> None:
        super().__init__(css_class="row " + css_class)