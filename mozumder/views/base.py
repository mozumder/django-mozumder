import time
import zlib
import logging
import pprint

from django.template import Context
from django.shortcuts import render
from django.views.generic import View, DetailView
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.middleware.csrf import get_token, _compare_masked_tokens
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.apps import apps

from dotmap import DotMap
import psycopg2

from mozumder.views import *
from .zip import Zip
from mozumder.template import MozumderHTMLMessageTemplate
from mozumder.template.default import templates_map
from .logging import LoggingHttpResponseNotFound, LoggingHttpResponseServerError, LoggingHttpResponseForbidden, LoggingHttpResponseBadRequest

logger = logging.getLogger("django")
pp = pprint.PrettyPrinter(indent=4)

#@method_decorator(csrf_exempt, name='dispatch')
class MozumderView(View,Zip):

    extra_context = {}
    vary = []
    try:
        CACHETIMEOUT = settings.CACHETIMEOUT
    except:
        CACHETIMEOUT = 1

    push_items = [
#       ['/static/fonts/woff/HelveticaNeueLTStd-UltLtEx.woff',
#       'font', 'font/woff'],
    ]
    
    preload = ", ".join(
        f'<{i[0]}>; rel=preload; as={i[1]}; type={i[2]}; crossorigin'
        for i in push_items)
        
    _lock = apps.get_app_config('mozumder')._lock

    def __init__(self, cache_key=None, *args, **kwargs):
        if cache_key:
            self.cache_key = cache_key
        else:
            self.cache_key = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def check_bot(self, user_agent):
        if user_agent == '':
            return True
        else:
            return any(e in user_agent for e in [
            'http','bot','spider','crawl','scan','grab',
            'ndex','search','seek','curl','site','slurp',
            'ruby','python','perl','java','lib','link',
            'get','windows nt 6','windows nt 5','liebaofast',
            'mb2345browser', 'zh-cn', 'micromessenger',
            'zh_cn', 'kinza'])
            #'get','mozilla/4.8 [en] (windows nt 6.0; u) ('])

    def start(self, request, id='', *args, **kwargs):
        self.request.perf_counter = time.perf_counter()
        self.request.timestamp = timezone.now()
        self.get_decompressor(request)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT')
        if user_agent:
            user_agent = user_agent.lower()
        else:
            user_agent = ''
        values = (
            f'django.contrib.sessionsSessionStore{settings.SECRET_KEY}',
            self.request.timestamp.isoformat(),
            self.request.COOKIES.get(settings.SESSION_COOKIE_NAME),
            ip,
            user_agent
        )
#        pp.pprint(values)
        # There appears to be some DB sort of race condition that prevents
        # data from being read. We keep retrying if this happens. There
        # should always be a result from the start_view prepared statement.
        with self._lock:
            self.c.execute(
                'EXECUTE start_view(%s, %s, %s, %s, %s);', values
            )
            result = self.c.fetchone()
            context = DotMap(result._asdict())
        if context.new_session == True:
            session_data = {
                'session_start_time':self.request.timestamp.isoformat()}
            expiry=result.session_expire_date
            self.request.session._set_session_key(context.session_key)
            self.request.session._cache.set(
                self.request.session.cache_key,
                session_data,
                self.request.session.get_expiry_age(
                    expiry=expiry))
#            self.request.session['session_start_time'] = \
#                self.request.timestamp.isoformat()
            self.request.session.new_session = True
            self.request.session.new_session_key = context.session_key
        else:
            self.request.session.update(context.session_data_field)
            self.request.session.new_session = False
        self.request.bot = self.check_bot(user_agent)
        self.request.session.modified = False
#        context.update(self.extra_context)

        self.pageKey = self.generate_cache_key(context)
        if id:
           self.pageKey = f"{self.pageKey}:{id}"

        return context, cache.get(self.pageKey), self.c

    def db_put(self, *args, **kwargs):
        self.session_start_time = self.request.timestamp.isoformat()
        self.request.bot = self.check_bot()

        csrf_token = self.request.POST.get('csrf', '')
        csrf_cookie = get_token(self.request)
        csrf_match = _compare_masked_tokens(csrf_token, csrf_cookie)

        if csrf_match:

            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                self.ip = x_forwarded_for.split(',')[0]
            else:
                self.ip = self.request.META.get('REMOTE_ADDR')
            self.post_db_query(*args, **kwargs)
            result = self.c.fetchone()
            if result.new_session == True:
                self.request.session._set_session_key(result.session_key)
                self.request.session['session_start_time'] = \
                    self.session_start_time
                self.request.session.new_session = True
            else:
                session_dict = self.request.session.decode(
                    result.session_data_field)
                self.request.session.update(session_dict)
                self.request.session.new_session = False
            self.request.session.modified = False
            return result.status_code, data
        else:
            return 403, {}

    def generate_cache_key(self, context):
        key = f'{settings.PROJECT_NAME}:{self.cache_key}'
        for vary in self.vary:
            id = getattr(context,vary)
            key = f'{key}:{context[vary]}'
        return key

class MozumderPageView(MozumderView):
    vary = []

    push_items = [
#       ['/static/fonts/woff/HelveticaNeueLTStd-UltLtEx.woff',
#       'font', 'font/woff'],
    ]

    preload = ", ".join(
        f'<{i[0]}>; rel=preload; as={i[1]}; type={i[2]}; crossorigin'
        for i in push_items)

    def response_generator(
            self,template, context,
            page_key=None, decompressor=None):
        """This is the critical core generator that creates the HTML of the
        page. It goes through each block of the template, and checks to see if
        it's already in the compressed cache. If it's not, it creates the HTML
        snd also compresses it and stores it in the cache. Meanwhile, it also
        creates a full-page HTML at the same time, and stores this full page
        HTML as a separate compressed cache item once the final block is done.
        """
        
        # Each template has a static compressed header zStart block that is
        # always sent, regardless of page context data. This is defined in the
        # template itself during startup __init__()
        zData = template.zStart

        compressor = False
        if decompressor:
            yield decompressor.decompress(zData)
        else:
            yield zData

        zPage = b''

        # Get all the currently cached blocks in the template.
        keys = {
            block.generate_cache_key(context):block
            for block in template.blocks}
        cached_blocks = cache.get_many(keys.keys())
        
        # Block tuples contain HTML generator & associated parameters, as well
        # as cache settings for each block. For every block, we will try to
        # retrieve it from the (compressed) cache. If it doesn't exist in the
        # cache, then we generate the block, and compress it and store it in
        # the cache.
        for key in keys:
            block = keys[key]

            if key in cached_blocks:
                zData = cached_blocks[key]
                if decompressor:
                    html = decompressor.decompress(zData)
            else:
                html = bytes(block.generate_html(context),'utf-8')
                # If there's no compressor due to there being no 'deflate' in
                # 'accept-encoding' header then create a new Zlib compressor
                # object. We will feed the compressor object a blank header
                # block, then feed it the real data in the next blocks,
                # which we will store in cache.
                if compressor == False:
                    compressor = zlib.compressobj(
                        level=self.level, wbits=self.wbits)
                    self.store(compressor,'zHeader',b"")
#                print(f"Setting block cache: {key}")
                zData = self.store(compressor,key,html,block.cache_time)

            zPage += zData
            if decompressor:
                yield html
            else:
                yield zData
        
        # Each template also has a static closing block, also created in the
        # templates __init__() function.
        zData = template.zEnd
        zPage += zData

        # After the last block, store the full page in the cache, then yield
        # the last block.
        
        # Temporary disable page cache
        if context.status_code == 200:
#            print(f"Setting page cache: {page_key}")
            cache.set(page_key, zPage, self.CACHETIMEOUT)
        if decompressor:
            yield decompressor.decompress(zData)
        else:
            yield zData

    def respond(self, request, template, context, zPageData):
        if zPageData is None:
            cache_hit = False
        else:
            cache_hit = True
            zPageData = template.zStart + zPageData
            if self.decompressor:
                zPageData = self.decompressor.decompress(zPageData)
        if context.status_code == 200:
            if cache_hit:
                return AnalyticHttpResponse(
                    zPageData,
                    status = context.status_code,
                    request=request,
                    cached=True)
            else:
                if settings.DEBUG:
                    return HttpResponse(
                        self.response_generator(
                            template, context,
                            self.pageKey, self.decompressor
                        ), status = context.status_code
                    )
                else:
                    return AnalyticStreamingHTTPResponse(
                        self.response_generator(
                            template, context,
                            self.pageKey, self.decompressor
                        ),
                        status = context.status_code,
                        request=request,
                        pageKey=self.pageKey
                    )
        
        if cache_hit == False:
            zPageData = b''.join(self.response_generator(
                            template, context,
                            self.pageKey, self.decompressor
                        ))

        if context.status_code == 404:
            return LoggingHttpResponseNotFound(
                zPageData,
                status = context.status_code,
                request=request,
                cached=cache_hit)
        elif context.status_code == 500:
            return LoggingHttpResponseServerError(
                zPageData,
                status = context.status_code,
                request=request,
                cached=cache_hit)
        elif context.status_code == 403:
            return LoggingHttpResponseForbidden(
                zPageData,
                status = context.status_code,
                request=request,
                cached=cache_hit)
        elif context.status_code == 400:
            return LoggingHttpResponseBadRequest(
                zPageData,
                status = context.status_code,
                request=request,
                cached=cache_hit)
        else:
            return AnalyticHttpResponse(
                zPageData, status = context.status_code,
                request=request, cached = cache_hit
            )


    def render(
        self, request, template,
        context=None, content_type=None,
        using=None, zPageData=None):
        
        response = self.respond(request, template, context, zPageData)

        if self.decompressor == None:
            response['content-encoding'] = 'deflate'
        if self.preload:
            response['link'] = self.preload
        if self.request.session.new_session == True:
            response.set_cookie(settings.SESSION_COOKIE_NAME,
                self.request.session.new_session_key,
                max_age=settings.SESSION_COOKIE_AGE,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE)
        response['Content-Security-Policy'] = template.csp

        return response

class MozumderJSONView(MozumderView):
    vary = []

    def __init__(self, cache_key=None, *args, **kwargs):
        if cache_key:
            self.cache_key = cache_key
        else:
            self.cache_key = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def json_response(self, id, request, cursor, context=None, zData=None):
    # Need to clean this up.
        if context.status_code != 200:
            json = bytes('{"status_code": '+ f'{context.status_code}' + '}','utf-8')
            if self.decompressor:
                zData = json
            else:
                compressor = zlib.compressobj(
                    level=self.level, wbits=self.wbits)
                self.store(compressor,'zHeader',b"")
                zData = compressor.compress(json)
                zData += compressor.flush(zlib.Z_FULL_FLUSH)
            response = AnalyticJSONResponse(zData,request=request, status=context.status_code, cached=False)
            if self.decompressor == None:
                response['content-encoding'] = 'deflate'
            return response

        cache_key = self.generate_cache_key(context) + f":{id}"

        if zData is None:
            view = self.view_function.view_name
            with self._lock:
                cursor.execute(f'EXECUTE {view}(%s);', [id])
                data = cursor.fetchone()
            compressor = zlib.compressobj(level=self.level, wbits=self.wbits)
            if data is None:
                context.status_code = 404
                json = bytes('{"status_code": '+
                    f'{context.status_code}' + '}','utf-8')
                zData = compressor.compress(json)
                zData += compressor.flush(zlib.Z_FULL_FLUSH)
            else:
                context.status_code = 200
                json = bytes(data[0],'utf-8')
#                print(f"Setting JSON cache: {cache_key}")
                zData = self.store(compressor,'%s' % (cache_key),
                    json,time=self.CACHETIMEOUT)
            cached = False
        else:
            if self.decompressor:
                json = self.decompressor.decompress(zData)
            cached = True
        if self.decompressor:
            zData = json
        response = AnalyticJSONResponse(
            zData,
            request=request,
            status=context.status_code,
            cached=cached)
        if self.decompressor == None:
            response['content-encoding'] = 'deflate'
        return response


    def get(self, request, id=0, *args, **kwargs):
        context, zJSONData, cursor = self.start(request,id)
        response = self.json_response(id,request,cursor,context,zJSONData)
        return response
