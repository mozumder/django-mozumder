from .template import Block, MozumderTemplate

class Error(Block):
    vary = ['message_hash']

    def generate_html(self,context=None):
        return f'<title>{context.title}</title></head><body><h1>Error!</h1><h2>Status Code: {context.status_code} {context.message}</h2><h2><a href="/">Homepage</a></h2>'

class MozumderErrorTemplate(MozumderTemplate):
    html_headers_include = 'error.html'
    inline_head_css_include = 'error.css'
    blocks=[Error()]
    def __init__(self, message):
        self.message = message
        super().__init__()
