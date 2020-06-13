from .component import code, Component

class raw(Component):

    def __init__(self,html="",css="",js="",openjs="",closejs=""):
        self.html = code(html)
        self.inline_head_css = code(css)
        self.inline_head_js = code(js)
        self.inline_bodyopen_js = code(openjs)
        self.inline_bodyclose_js = code(closejs)
