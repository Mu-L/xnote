import typing

from .base import BaseComponent, BaseContainer
from xnote.core import xtemplate
from .component import ConfirmButton, ActionButton, TextTag, escape_html
from xnote.core import xconfig

class ListViewItem(BaseComponent):
    # 是否展示右箭头
    show_chevron_right = False
    # 操作按钮
    action_btn : typing.Optional[ActionButton] = None
    # 操作部分
    action_html = ""
    # 标签列表
    tags: typing.List[TextTag]
    # 默认链接在外部
    is_link_outside = True

    _outside_html = """
<div class="list-item no-padding">
    <a class="list-item-link {{item.css_class}}" href="{{ item.href }}">
        {% if item.icon_class %}
            <i class="{{item.icon_class}}"></i>
        {% end %}
        <span>{{ item.text }}</span>
        {% for tag in item.tags %} {% render tag %} {% end %}
        <div class="float-right">
            <span class="badge-info">{{ item.badge_info }}</span>
            {% if item.action_btn %}
                {% render item.action_btn %}
            {% end %}
            {% raw item.action_html %}
            {% if item.show_chevron_right %}
                <i class="fa fa-chevron-right"></i>
            {% end %}
        </div>
    </a>
</div>
"""

    _inside_html = """
<div class="list-item {{item.css_class}}">
    {% if item.icon_class %}
        <i class="{{item.icon_class}}"></i>
    {% end %}
    <span>{{item.text}}</span>
    {% for tag in item.tags %} {% render tag %} {% end %}
    <div class="float-right">
        <span class="badge-info">{{ item.badge_info }}</span>
        {% if item.action_btn %}
            {% render item.action_btn %}
        {% end %}
        {% raw item.action_html %}
        {% if item.show_chevron_right %}
            <i class="fa fa-chevron-right"></i>
        {% end %}
    </div>
</div>
"""

    _outside_code = xtemplate.compile_template(_outside_html)
    _intside_code = xtemplate.compile_template(_inside_html)

    def __init__(
            self, text="", href="", icon_class="", badge_info="", 
            show_chevron_right = False, action_html = "",
            css_class="") -> None:
        self.text = text
        self.css_class = css_class
        self.icon_class = icon_class
        self.href = xconfig.WebConfig.resolve_path(href)
        self.badge_info = badge_info
        self.show_chevron_right = show_chevron_right
        self.tags = []
        self.action_html = action_html

        if href == "":
            self.is_link_outside = False

    def render(self):
        if self.is_link_outside:
            return self._outside_code.generate(item = self)
        else:
            return self._intside_code.generate(item = self)

class _ListViewOption:

    def __init__(self, name="", value=""):
        self.name = name
        self.value = value

class ListViewDropdown(BaseComponent):

    _code = xtemplate.compile_template("""
<div class="list-item {{item.css_class}}">

{% if item.icon_class %}
    <i class="{{item.icon_class}}"></i>
{% end %}

    <span>{{ item.text }}</span>
                                       
{% for tag in item.tags %} {% render tag %} {% end %}
<div class="float-right">
    <select name="{{item.name}}" data-type="{{item.data_type}}" value="{{item.value}}">
        {% for option in item.options %}
            <option value="{{option.value}}">{{option.name}}</option>
        {% end %}
    </select>
    {% if item.show_chevron_right %}
        <i class="fa fa-chevron-right"></i>
    {% end %}
</div>

</div>
""")
    
    show_chevron_right = False
    # 标签列表
    tags: typing.List[TextTag]

    icon_class = ""
    css_class = ""
    
    def __init__(self, text="", name="", data_type="int", value=""):
        self.text = text
        self.name = name
        self.data_type = data_type
        self.value = value
        self.tags = []
        self.options = []

    def add_option(self, name="", value=""):
        self.options.append(_ListViewOption(name=name, value=value))

    def render(self):
        return self._code.generate(item = self)

class ListView(BaseContainer):    
    _code = xtemplate.compile_template("""
{% if len(item_list) == 0 %}
    {% include common/text/empty_text.html %}
{% end %}

{% for item in item_list %}
    {% render item %}
{% end %}
""")
    
    def add_item(self, item: ListViewItem):
        self.add(item)

    def render(self):
        return self._code.generate(item_list = self.children)
    
    def add_dropdown(self, text="", name="", data_type="int", value=""):
        dropdown = ListViewDropdown(text=text, name=name, data_type=data_type, value=value)
        self.add(dropdown)
        return dropdown

ItemList = ListView
ListItem = ListViewItem
