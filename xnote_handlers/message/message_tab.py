from xnote.plugin import TabBox
from .dao import get_message_stat


def get_message_tab(user: str, tab_default="log"):
    stat = get_message_stat(user)
    tab = TabBox(tab_key="tag", tab_default=tab_default, css_class="card message-tab")
    tab.add_item(f"记事({stat.log_count})", value="log", href="/message?tag=log")
    tab.add_item(f"标签({stat.key_count})", value="log.tags", href="/message/tag/list")
    tab.add_item(f"日期", value="log.date", href="/message/dairy?tag=log.date")
    return tab
