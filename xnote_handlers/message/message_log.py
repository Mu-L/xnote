# encoding=utf-8

import xutils


from xutils import Storage
from xutils import webutil
from xutils import netutil
from xnote.core import xauth
from xnote.core import xtemplate
from xnote.core.xtemplate import T
from xnote.plugin import TabBox
from xnote_handlers.message import message_utils
from xnote_handlers.message import message_tag
from xnote_handlers.message.message_utils import filter_key
from .dao_template import MessageTemplateDao
from .message_utils import mark_filter_text
from xnote.core.xnote_user_config import UserConfig

class LogPageHandler:

    def do_get(self):
        key = xutils.get_argument_str("key", "")
        input_tag = xutils.get_argument_str("tag", "log")
        user_name = xauth.current_name_str()
        user_id = xauth.current_user_id()
        default_content = filter_key(key)

        kw = Storage()

        kw.tag=input_tag
        kw.message_tag=input_tag
        kw.search_type="message"
        kw.show_system_tag=False
        kw.show_side_system_tags=True
        kw.show_sub_link=False
        kw.html_title=T("随手记")
        kw.default_content=default_content
        kw.show_back_btn=False
        kw.message_tab="log"
        kw.message_placeholder="记录发生的事情/产生的想法"
        kw.side_tags=message_utils.list_hot_tags(user_name, 20)
        kw.search_ext_dict = dict(tag="log.search")
        kw.message_left_class = "hide"
        kw.message_right_class = "row"
        
        filter_content = UserConfig.msg_filter.get_str(user_id=user_id)
        kw.show_tag_filter = True
        kw.filter_config_key = UserConfig.msg_filter.key
        kw.filter_html = mark_filter_text(filter_content, link_type="log", selected_key=key).result_text
        self.handle_template_tab(kw, default_content)
        
        return xtemplate.render("message/page/message_list_view.html", **kw)
    
    def handle_template_tab(self, kw: Storage, default_content: str):
        template_content = ""
        user_id = xauth.current_user_id()
        template_id = xutils.get_argument_int("template_id")
        template_list = MessageTemplateDao.list_by_user(user_id=user_id)
        template_tab = TabBox(tab_key = "template_id", tab_default="0", css_class="btn-style")
        if len(template_list) == 0:
            template_tab.add_item(title="默认", value="0")
        else:
            template_content = template_list[0].content
            template_tab.tab_default = str(template_list[0].template_id)

            for template in template_list:
                template_tab.add_item(title=template.name, value=str(template.template_id))
                if template.template_id == template_id:
                    template_content = template.content
                    template_tab.tab_default = str(template_list[0].template_id)
        
        kw.message_template_tab = template_tab
        if default_content == "":
            kw.default_content = template_content