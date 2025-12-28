from xnote.core import xtemplate

class AsideConfig:
    @classmethod
    def get_default_aside_html(cls):
        return xtemplate.render("common/sidebar/default.html")

    @classmethod
    def get_fs_aside_html(cls):
        return xtemplate.render("fs/component/fs_sidebar.html")

    @classmethod
    def get_admin_aside_html(cls):
        return xtemplate.render("system/component/admin_nav.html")

    @classmethod
    def get_settings_aside_html(cls):
        return xtemplate.render("settings/page/settings_sidebar.html")
