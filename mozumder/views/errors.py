import time
import logging
import traceback
import sys

from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.db import connection
import psycopg2
from django.core.cache import cache
from django.http import Http404

from dotmap import DotMap
from .base import MozumderView, MozumderPageView
from ..template import MozumderErrorTemplate
from django.urls import Resolver404
import pprint
pp = pprint.PrettyPrinter(indent=4)
def myhash(s):
    return binascii.b2a_base64(struct.pack('i', hash(s)))
logger = logging.getLogger()

class MozumderErrorView(MozumderPageView):
    status_code = 404
    template = MozumderErrorTemplate('Error')
    vary = ['message_hash']
    def render_error(self, title=None, *args, **kwargs):
        self.request.perf_counter = time.perf_counter()
        self.request.timestamp = timezone.now()
        self.get_decompressor(self.request)
        user_agent = self.request.META.get('HTTP_USER_AGENT')
        if user_agent:
            user_agent = user_agent.lower()
        else:
            user_agent = ''
        with self._lock:
            self.c.execute(
                'EXECUTE get_session(%s);', [self.request.COOKIES.get(settings.SESSION_COOKIE_NAME)]
            )
            result = self.c.fetchone()
            if result:
                context = DotMap(result._asdict())
            else:
                context = DotMap({})
        context.message = self.request.message
        context.message_hash = hash(self.request.message)
        context.title = title
        self.request.session.update(context.session_data_field)
        self.request.session.new_session = False
        self.request.bot = self.check_bot(user_agent)
        self.request.session.modified = False
        self.pageKey = self.generate_cache_key(context)
        zPageData = cache.get(self.pageKey)
        context.status_code = self.status_code
        context.update(self.extra_context)
        return self.render(self.request, self.template,
            context=context, zPageData=zPageData)

    def dispatch(self, request, *args, **kwargs):
        return self.render_error(*args, **kwargs)

class page_not_found_view(MozumderErrorView):
    c = connection.cursor().connection.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
    status_code = 404
    template = MozumderErrorTemplate('Oh noes! Not Found')
    def dispatch(self, request, *args, exception=None, **kwargs):
        if isinstance(exception, Resolver404):
            self.request.message = self.template.message
        elif isinstance(exception, Http404):
            self.request.message = exception.args[0]
        else:
            self.request.message = self.template.message
        return self.render_error(title='404 Not Found', *args, **kwargs)

class error_view(MozumderErrorView):
    c = connection.cursor().connection.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
    status_code = 500
    template = MozumderErrorTemplate('Internal Server Error')
    def dispatch(self, *args,**kwargs):
        type, value, tb = sys.exc_info()
        logger.error('Internal Server Error!')
        logger.error(f'- Specifically, {value}')
        logger.error('- Please review the most recent stack entries:')
        logger.error(''.join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
        self.request.message = self.template.message
        return self.render_error('500 Internal Server Error', *args, **kwargs)

class permission_denied_view(MozumderErrorView):
    c = connection.cursor().connection.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
    status_code = 403
    template = MozumderErrorTemplate('Permission Denied')
    def dispatch(self, request, *args, exception=None, **kwargs):
        return self.render_error(title='403 Permission Denied', *args, **kwargs)
class bad_request_view(MozumderErrorView):
    c = connection.cursor().connection.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
    status_code = 400
    template = MozumderErrorTemplate('Bad Request')
    def dispatch(self, request, *args, exception=None, **kwargs):
        return self.render_error(title='400 Bad Request', *args, **kwargs)
