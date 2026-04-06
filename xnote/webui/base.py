import typing
from xutils.textutil import safe_str

class BaseComponent:
    """UI组件的基类"""
    def render(self):
        return ""

class BaseContainer(BaseComponent):
    def __init__(self, css_class=""):
        self.css_class = css_class
        self.children = [] # type: list[BaseComponent]

    def add(self, item: BaseComponent):
        self.children.append(item)
        return self

    def set_children(self, children: typing.List[BaseComponent]):
        self.children = children

    def is_empty(self):
        return len(self.children) == 0

    def render(self):
        if self.is_empty():
            return ""
        out = []
        out.append(f"""<div class="{self.css_class}">""")
        for item in self.children:
            item_html = safe_str(item.render())
            out.append(item_html)
        out.append("""</div>""")
        return "".join(out)
