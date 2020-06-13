import pprint
import psycopg2
from django.http import Http404

from .base import MozumderView, MozumderPageView, MozumderJSONView

pp = pprint.PrettyPrinter(indent=4)

class MozumderIndexView(MozumderPageView):

    def get(self, request, *args, **kwargs):
        context, zPageData, cursor = self.start(request)
        if hasattr(self,'view_function'):
            if not zPageData:
                with self._lock:
                    self.view_function.execute(cursor)
                    result = cursor.fetchone()
                    if result != None:
                        context.update(result._asdict())
                        context.status_code = 200
                        context.message = 'OK'
                    else:
                        raise Http404("Item not found")
            else:
                context.status_code = 200
                context.message = 'OK'
        else:
            context.status_code = 200
            context.message = 'OK'
        context.update(self.extra_context)
        return (self.render(request, self.template,
            context=context, zPageData=zPageData))

class MozumderDetailView(MozumderPageView):

    def get(self, request, slug, *args, **kwargs):
        context, zPageData, cursor = self.start(request,id=slug)
        if not zPageData:
            with self._lock:
                self.view_function.execute(cursor, id=slug)
                result = cursor.fetchone()
                if result != None:
                    context.update(result._asdict())
                    context.status_code = 200
                    context.message = 'OK'
                else:
                    raise Http404("Item not found")
        else:
            context.status_code = 200
            context.message = 'OK'
        context.update(self.extra_context)
        return (self.render(request, self.template,
            context=context, zPageData=zPageData))

class MozumderListView(MozumderPageView):

    def get(self, request, slug, *args, **kwargs):
        context, zPageData, cursor = self.start(request,id=slug)
        if not zPageData:
            with self._lock:
                self.view_function.execute(cursor, slug)
                result = cursor.fetchall()
                if result:
                    context.data = result
                    context.status_code = 200
                    context.message = 'OK'
                else:
                    raise Http404("List not found")
        else:
            context.status_code = 200
            context.message = 'OK'
        context.update(self.extra_context)
        return (self.render(request, self.template,
            context=context, status=status, zPageData=zPageData))

class MozumderCreateView(MozumderListView):

    def post(self, request, *args, **kwargs):
        self.start_timer()
        status, context = self.db_put()
        return self.render(request, self.get_template)

    def post_db_query(self, *args, **kwargs):
        self.c.execute('EXECUTE {self.post_sql}(%s, %s, %s, %s, %s);',
            self.base_db_parameters())

class MozumderUpdateView(MozumderDetailView):

    def post(self, request, *args, **kwargs):
        self.start_timer()
        status, context = self.db_put()
        return (self.render(request, self.get_template,
            context=context, status=status))

    def post_db_query(self, id, *args, **kwargs):
        self.c.execute(f'EXECUTE {self.post_sql}(%s, %s, %s, %s, %s, %s);',
            [id] + self.base_db_parameters())


class MozumderJSONDetailView(MozumderJSONView):

    pass
