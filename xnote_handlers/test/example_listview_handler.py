import xutils
import copy

from xutils import webutil, Storage
from xnote.plugin.list_plugin import BaseListPlugin, BasePlugin
from xnote.plugin.list import ListView, ListViewItem, ListItem, TextTag
from xnote.plugin.component import ConfirmButton, BaseContainer, ActionButton
from xnote_handlers.config import LinkConfig
from .example_handler import get_example_tab

class ListPluginHandler(BaseListPlugin):
    title = "ListPlugin示例"
    parent_link = LinkConfig.develop_index

    tab_html = """
<div class="card">
    {% render example_tab %}
</div>
"""

    def handle_page(self):
        list_view = self.create_list_view()

        for i in range(1, 6):
            action_html = """
<a>编辑</a>
<a class="link danger">删除</a>
"""
            list_view.add_item(ListViewItem(
                text=f"row{i}", badge_info="test", 
                icon_class="fa fa-file-text-o",
                action_html=action_html,
                show_chevron_right=True))

        kw = Storage()
        kw.list_view = list_view
        kw.page_current = 1
        kw.page_total = 100
        kw.page_url = "?page="

        self.writehtml(self.tab_html, example_tab = get_example_tab(tab_default="list_plugin"))
        return self.response_page(**kw)
    


class ListExampleHandler(BasePlugin):
    parent_link = LinkConfig.develop_index
    title = "ListView示例"
    rows = 0
    body_html = """
{% include test/component/example_nav_tab.html %}

<div class="card">
    <span class="card-title">ListView: 外层链接</span>
    {% render item_list %}
</div>

<div class="card">
    <span class="card-title">ListView: 内层链接</span>
    {% render item_list2 %}
</div>
"""
    def handle(self, input=""):
        item_list = ListView()
        item_list2 = ListView()

        action = xutils.get_argument_str("action")
        if action == "delete":
            return self.handle_delete()

        for index in range(5):
            text = f"物品-{index+1}"
            item = ListItem(text=text, href=f"javascript:xnote.alert({index+1})", badge_info=f"徽标{index+1}")
            item.show_chevron_right = True
            if index % 2 == 0:
                item.icon_class = "fa fa-file-text-o"
            else:
                item.icon_class = "fa fa-list"
                item.tags.append(TextTag(text="标签", css_class="lightblue"))
                item.tags.append(TextTag(text="标签2", css_class="orange"))
            item.action_btn = ConfirmButton(text="删除", url="?action=delete", message=f"确认删除[{text}]吗", css_class="btn danger")
            
            item_list.add_item(item)

            item2 = copy.deepcopy(item)
            item2.is_link_outside = False
            item2.show_chevron_right = False
            item_list2.add_item(item2)

        kw = Storage()
        kw.item_list = item_list
        kw.item_list2 = item_list2
        kw.example_tab = get_example_tab()

        self.writehtml(html=self.body_html, **kw)

    def handle_delete(self):
        return webutil.FailedResult(code="500", message="mock删除失败")

xurls = (
    r"/test/example/list", ListExampleHandler,
    r"/test/example/list_plugin", ListPluginHandler,
)