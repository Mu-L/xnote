import typing

from typing import List
from xutils.textutil import safe_str

class BaseComponent:
    """UI组件的基类"""
    def render(self) -> str:
        return ""

class BaseContainer(BaseComponent):
    def __init__(self, css_class="", css_style=""):
        self.css_class = css_class
        self.css_style = css_style
        self.children: List[BaseComponent] = []

    def add(self, item: BaseComponent):
        self.children.append(item)
        return self

    def set_children(self, children: List[BaseComponent]):
        self.children = children

    def is_empty(self):
        return len(self.children) == 0

    def render(self) -> str:
        # TODO: 防止递归
        if self.is_empty():
            return ""
        css_style_attr = ""
        if self.css_style:
            css_style_attr = f'style="{self.css_style}"'
        out = []
        out.append(f"""<div class="{self.css_class}" {css_style_attr}>""")
        for item in self.children:
            item_html = safe_str(item.render())
            out.append(item_html)
        out.append("""</div>""")
        return "".join(out)

Div = BaseContainer
