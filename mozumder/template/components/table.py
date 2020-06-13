from .component import code, Component

class tableHTML(code):
    def __iter__(self,request,context):
        yield "<table>"
        if request.user.is_authenticated:
            for row in context.articles_list:
                yield f'<tr><td class="fixed">{row.date_published:%B %d, %Y}</td><td><a href="/{row.slug}">{row.title}</a></td><td><a href="edit">edit</a><td><a href="delete">delete</a></td></tr>'
        else:
            for row in context.articles_list:
                yield f'<tr><td>{row.date_published:%B %d, %Y}</td><td><a href="/{row.slug}">{row.title}</a></td></tr>'
        yield "</table>"

class tableCSS(code):
    def __iter__(self,request=None,context=None):
        yield "table {border:0};"

class table(Component):
    def __init__(self):
        super().__init__()
        self.html = tableHTML()
        self.inline_head_css = tableCSS()

