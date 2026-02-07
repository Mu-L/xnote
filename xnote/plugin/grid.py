from .base import BaseContainer, BaseComponent
from xnote.core import xtemplate

class AppInfo(BaseComponent):
    _template = xtemplate.compile_template("""
<a class="grid-item" href="{{info.url}}"> 
    {% if info.img_src %}
        <div class="app-icon img-box">
            <img src="{{info.img_src}}">
        </div>
    {% else %}
        <div class="app-icon">
            <i class="fa fa-{{info.icon}} {{info.icon}}"></i>
        </div>
    {% end %}
    <span>{{T(info.name)}}</span>
</a>
""", name="xnote.plugin.app_info")
    
    def __init__(self, name="", url = "", icon="", img_src= "", css_class=""):
        self.name = name
        self.url = url
        self.icon = icon
        self.img_src = img_src
        self.css_class = css_class
        
    def render(self):
        return self._template.generate(info = self, T = xtemplate.T)

class AppGrid(BaseContainer):
    def __init__(self, css_class=""):
        super().__init__()
        self.css_class = css_class
    
    def add_app(self, app_info: AppInfo):
        self.add(app_info)
    
    
    
