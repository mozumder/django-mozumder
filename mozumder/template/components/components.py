from .component import code, Component

class componentsHTML(code):
    def __init__(self, data):
        self.data = data
    def __iter__(self, request, context=None):
        for i in self.data:
            yield from i.html.send(request, context)

class componentsCSS(code):
    def __init__(self,data):
        self.data = data
    def __iter__(self, request, context=None):
        for i in self.data:
            yield from i.inline_head_css.send(request, context)

class Components(Component):

    def __init__(self,componentslist):
        super().__init__()
        self.data = componentslist
        self.html = componentsHTML(componentslist)
        self.inline_head_css = componentsCSS(componentslist)


