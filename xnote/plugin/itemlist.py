from .base import BaseComponent, BaseContainer

class _ListItem(BaseComponent):
    """TODO 开发中"""

    # 是否展示右箭头
    show_chevron_right = False

    def __init__(self, text="", href="", icon_class="", badge_info="") -> None:
        self.text = text
        self.icon_class = icon_class
        self.href = href
        self.badge_info = badge_info

class _ItemList(BaseContainer):
    """TODO 开发中"""
    pass

