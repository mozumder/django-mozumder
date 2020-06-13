from .component import code, Component

class divHTML(code):
    def __iter__(self,request,context=None):
        yield "<div>"
        if self.data:
            yield from self.data.html.send(request,context)
        yield "</div>"

class divCSS(code):
    def __iter__(self,request,context=None):
        if self.data:
            yield from self.data.inline_head_css.send(request,context)

class divJS(code):
    def __iter__(self,request,context=None):
        if self.data:
            yield from self.data.inline_head_js.send(request,context)

class divOpenJS(code):
    def __iter__(self,request,context=None):
        if self.data:
            yield from self.data.inline_bodyopen_js.send(request,context)

class divCloseJS(code):
    def __iter__(self,request,context=None):
        if self.data:
            yield from self.data.inline_bodyclose_js.send(request,context)

class div(Component):
    
    def __init__(self,component=None):
        super().__init__()
        self.html = divHTML(component)
        self.inline_head_css = divCSS(component)
        self.inline_head_js = divJS(component)
        self.inline_bodyopen_js = divOpenJS(component)
        self.inline_bodyclose_js = divCloseJS(component)
