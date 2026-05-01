from typing import Optional
from .component import BaseComponent, BaseContainer
from .utils import build_data_attrs

class Image(BaseComponent):
    
    def __init__(self, src="", alt="", width="", height="", css_class="", css_style="", data_dict:Optional[dict] = None) -> None:
        self.src = src
        self.alt = alt
        self.width = width
        self.height = height
        self.css_class = css_class
        self.css_style = css_style
        self.data_dict = data_dict
    
    def render(self) -> str:
        data_attrs = build_data_attrs(self.data_dict)
        return f"""<img src="{self.src}" width="{self.width}" height="{self.height}" class="{self.css_class}" style="{self.css_style}" {data_attrs}>"""
    
class ImageRow(BaseContainer):
    """图片行,包括图片和文字"""
    pass
