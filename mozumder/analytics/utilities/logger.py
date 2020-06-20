import multiprocessing
import threading
import os
import logging
import time
import pickle
import inspect
import socket

from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

import psycopg2

from user_agents import parse as parse_ua

from ..__init__ import *
from ..signals import *

try:
    import uwsgi
    import uwsgidecorators
    uwsgi_mode = True
except:
    uwsgi_mode = False

message_log = logging.getLogger("django")
database_log = logging.getLogger("database")
access_log = logging.getLogger("access")

class logMessage:
    timestamp = None
    ip = None
    response_time = None
    status_code = None
    url = None
    request_content_type = None
    request_method = None
    ajax = False
    preview = False
    prefetch = False
    referer = None
    user_agent = None
    request_content_length = 0
    accept = None
    accept_language = None
    accept_encoding = None
    response_content_type = None
    response_content_length = 0
    compress = None
    session_key = None
    user_id = None
    latitude = None
    longitude = None
    protocol = None
    cached = False
    session_start_time = None


class LogWriter():
    log_sql = 'log'
    def __init__(self, cursor=None, lock=None):
        self.cursor = cursor
        self._lock = lock

    def threaded_write(self, msg=None):
        self.write(self.cursor, self._lock, msg)

    @staticmethod
    def write(cursor, lock, msg=None):
        if uwsgi_mode:
            msg = pickle.loads(msg)
#        msg = self.msg

        if msg.cached:
            cached = '*'
        else:
            cached = ''
        if msg.compress:
            compress = '*'
        else:
            compress = ''
        if hasattr(settings,'ROOT_URL'):
            if msg.url.startswith(settings.ROOT_URL):
                url = msg.url[len(settings.ROOT_URL):]
            else:
                url = msg.url
            if msg.referer:
                if msg.referer.startswith(settings.ROOT_URL):
                    referer = msg.referer[len(settings.ROOT_URL):]
                else:
                    referer = msg.referer
            else:
                referer = '*'
        else:
            url = msg.url
            if msg.referer:
                referer = msg.referer
            else:
                referer = '*'
        if msg.user_id:
            user_id = msg.user_id
        else:
            user_id = '-'

        if msg.bot:
            bot = '*'
        else:
            bot = ''

        if METHOD_CHOICES_DICT[msg.request_method] == 'GET':
            method = '-'
        elif METHOD_CHOICES_DICT[msg.request_method] == 'POST':
            method = '+'
        else:
            method = '?'
        if msg.ajax:
            direction = f'<{method}'
        else:
            direction = f'{method}>'

        ua_string = msg.user_agent[:252] + (msg.user_agent[252:] and '..') if msg.user_agent else None
        if ua_string:
            user_agent = parse_ua(ua_string)
        else:
            user_agent = parse_ua('')
            msg.bot = True
        if len(user_agent.browser.version) > 0:
            browser_major_version = user_agent.browser.version[0]
        else:
            browser_major_version = None
        if len(user_agent.browser.version) > 1:
            browser_minor_version = user_agent.browser.version[1]
        else:
            browser_minor_version = None
        if len(user_agent.browser.version) > 2:
            browser_patch = user_agent.browser.version[2]
        else:
            browser_patch = None
        if len(user_agent.os.version) > 0:
            os_major_version = user_agent.os.version[0]
        else:
            os_major_version = None
        if len(user_agent.os.version) > 1:
            os_minor_version = user_agent.os.version[1]
        else:
            os_minor_version = None
        if len(user_agent.os.version) > 2:
            os_patch = user_agent.os.version[2]
        else:
            os_patch = None
        if len(user_agent.os.version) > 3:
            os_minor_patch = user_agent.os.version[3]
        else:
            os_minor_patch = None
        fields = [
                    msg.timestamp,
                    msg.ip,
                    msg.response_time,
                    msg.status_code,
                    msg.url[:508] + (msg.url[508:] and '..') if msg.url else None,
                    msg.request_content_type[:48] + (msg.request_content_type[48:] and '..') if msg.request_content_type else None,
                    msg.request_method,
                    msg.ajax,
                    msg.referer[:508] + (msg.referer[508:] and '..') if msg.referer else None,
                    ua_string,
                    msg.request_content_length,
                    msg.accept[:252] + (msg.accept[252:] and '..') if msg.accept else None,
                    msg.accept_language[:48] + (msg.accept_language[48:] and '..') if msg.accept_language else None,
                    msg.accept_encoding[:48] + (msg.accept_encoding[48:] and '..') if msg.accept_encoding else None,
                    msg.response_content_type[:48] + (msg.response_content_type[48:] and '..') if msg.response_content_type else None,
                    msg.response_content_length,
                    msg.compress,
                    msg.session_key,
                    msg.user_id,
                    msg.latitude,
                    msg.longitude,
                    msg.protocol,
                    msg.cached,
                    msg.session_start_time,
                    msg.preview,
                    msg.prefetch,
                    msg.bot,
                ]
        with lock:
        
            try:
                cursor.execute("execute " + LogWriter.log_sql + "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", fields)
                result = cursor.fetchone()

            except psycopg2.errors.StringDataRightTruncation:
                message_log.error("Log entry contains too many characters in fields. Please review fields:")
                count = 0
                for i in fields:
                    message_log.error(f'{c}: length {len(i)}: {i}')
            host = None
            cursor.execute('execute get_host(%s);' , [result.ip_id])
            host_result = cursor.fetchone()
            if host_result.hostname:
                host = host_result.hostname
                if host_result.domain_id == None:
                    names = host.split(".")[1:]
                    if names:
                        domain = names[-1]
                        if len(names) > 1:
                            domain = names[-2] + '.' + domain
                        if len(names) > 2:
                            domain = names[-3] + "." + domain
                        try:
                            cursor.execute('execute create_domain(%s, %s);' ,
                            [domain, msg.bot])
                        except psycopg2.errors.StringDataRightTruncation:
                            message_log.error("Log create_domain entry contains too many characters for domain name.")
                            message_log.error(f'length {len(domain)}: {domain}')

                        domain_result = cursor.fetchone()
                        if domain_result:
                            cursor.execute('execute update_host_domain(%s, %s);' ,
                                [host_result.host_id, domain_result.id])
                    else:
                        domain = '-'
                else:
                    domain = host_result.domainname
            else:
                host = None
                try:
                    host = socket.gethostbyaddr(msg.ip)[0]
                except:
                    domain = '-'
                if host:
                    names = host.split(".")[1:]
                    if len(names) <= 1:
                        message_log = logging.warning(f"No hostname found for host {host}")
                        names = host.split(".")
                    domain = names[-1]
                    if len(names) > 1:
                        domain = names[-2] + '.' + domain
                    if len(names) > 2:
                        domain = names[-3] + "." + domain
                    cursor.execute('execute create_domain(%s, %s);' ,
                        [domain, msg.bot])
                    domain_result = cursor.fetchone()
                    if domain_result:
                        if host_result.host_id != None:
                            cursor.execute('execute update_host_domain(%s, %s);' ,
                                [host_result.host_id, domain_result.id])
                        else:
                            try:
                                cursor.execute('execute update_host(%s, %s, %s, %s);' ,
                                    [result.ip_id, domain_result.id, host, msg.bot])
                            except psycopg2.errors.StringDataRightTruncation:
                                message_log.error("Log update_host entry contains too many characters for host name!")
                                message_log.error(f'length {len(host)}: {host}')

            cursor.execute('execute get_user_agent(%s);' , [result.user_agent_id])
            useragent_result = cursor.fetchone()
            if useragent_result:
                if useragent_result.browser_id is None:
                    cursor.execute(
                        'execute update_browser(%s, %s, %s, %s, %s);' ,
                        [
                            result.user_agent_id,
                            user_agent.browser.family,
                            browser_major_version,
                            browser_minor_version,
                            browser_patch,
                        ])

                if useragent_result.os_id is None:
                    cursor.execute(
                        'execute update_os(%s, %s, %s, %s, %s, %s);' ,
                        [
                            result.user_agent_id,
                            user_agent.os.family,
                            os_major_version,
                            os_minor_version,
                            os_patch,
                            os_minor_patch,
                        ])

                if useragent_result.device_id is None:
                    cursor.execute(
                        'execute update_device(%s, %s, %s, %s, %s, %s, %s, %s, %s);' ,
                        [
                            result.user_agent_id,
                            user_agent.device.family,
                            user_agent.device.brand,
                            user_agent.device.model,
                            user_agent.is_mobile,
                            user_agent.is_pc,
                            user_agent.is_tablet,
                            user_agent.is_touch_capable,
                            user_agent.is_bot
                        ])

            cursor.execute('execute record_timestamp(%s);', [ result.id ])
            log_timestamp_result = cursor.fetchone()

        if user_agent.browser.family != 'Other':
            browser = f'{user_agent.browser.family}'
            if browser_major_version != None:
                browser = f'{browser} {browser_major_version}'
            if browser_minor_version != None:
                browser = f'{browser}.{browser_minor_version}'
            if user_agent.os.family == 'Other':
                os = ''
            else:
                os = f', {user_agent.os.family}'
                if os_major_version != None:
                    os = f'{os} {os_major_version}'
                if os_minor_version != None:
                    os = f'{os}.{os_minor_version}'
            bot = ''
            device = ''
            if user_agent.device.family in [
                'Spider', 'Generic Smartphone', 'Generic Desktop']:
                bot = '*'
            elif user_agent.device.family != 'Other':
                if user_agent.device.brand:
                    device = f', {user_agent.device.brand}'
                    if user_agent.device.model:
                        device = f'{device} {user_agent.device.model}'
                else:
                    device = f', {user_agent.device.family}'
            ua = f'({browser}{os}{device}){bot}'
        else:
            if ua_string == '':
                ua = '(Empty User Agent)'
            else:
                ua = f'({ua_string})*'

        timestamp = timezone.localtime(result.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        log_response_time = (log_timestamp_result.log_timestamp-result.timestamp).microseconds/1000
#        log_response_time = (time.perf_counter()-msg.perf_counter)*1000
        log_delay = log_response_time - result.response_time
        access_log.info(
            f'{msg.ip} '
            f'{domain} '
            f'{user_id} '
            f'{result.response_time:.3f}ms{cached} '
            f'{log_delay:.3f}ms '
            f'{msg.response_content_length}b{compress} '
            f'{msg.status_code} '
            f'{referer} {direction} {url} '
            f'{ua} '
        )
        
    @staticmethod
    def create_log_message(response):
    
        msg = logMessage()

        msg.timestamp = response.request.timestamp
        msg.perf_counter = response.request.perf_counter
        msg.response_time = (time.perf_counter()-response.request.perf_counter)*1000
        msg.ip = response.get_client_ip(response.request)
        if 'REQUEST_METHOD' in response.request.META:
            method = response.request.META['REQUEST_METHOD']
            if method in METHOD_CHOICES_LOOKUP:
                msg.request_method = METHOD_CHOICES_LOOKUP[method]
            else:
                msg.request_method = UNKNOWN
        else:
            msg.request_method = UNKNOWN
        msg.url = response.request.build_absolute_uri()
        msg.ajax = response.request.is_ajax()
        purpose = response.request.META.get('HTTP_X_PURPOSE')
        moz = response.request.META.get('HTTP_X_MOZ')
        if purpose:
            if purpose.lower() == 'preview':
                msg.preview = True
                msg.prefetch = False
            elif purpose.lower() == 'prefetch':
                msg.preview = False
                msg.prefetch = True
            else:
                msg.preview = False
                msg.prefetch = False
        elif moz:
            if moz.lower() == 'preview':
                msg.preview = True
                msg.prefetch = False
            elif moz.lower() == 'prefetch':
                msg.preview = False
                msg.prefetch = True
            else:
                msg.preview = False
                msg.prefetch = False
        else:
            msg.preview = False
            msg.prefetch = False
        msg.bot = response.request.bot
        msg.accept = response.request.META.get('HTTP_ACCEPT')
        msg.accept_language = response.request.META.get('HTTP_ACCEPT_LANGUAGE')
        msg.accept_encoding = response.request.META.get('HTTP_ACCEPT_ENCODING')
        msg.referer = response.request.META.get('HTTP_REFERER')
        msg.user_agent = response.request.META.get('HTTP_USER_AGENT')
        if 'CONTENT_TYPE' in response.request.META:
            msg.request_content_type = response.request.META['CONTENT_TYPE']
        else:
            msg.request_content_type = None
        if 'CONTENT_LENGTH' in response.request.META.keys():
            if response.request.META['CONTENT_LENGTH']:
                msg.request_content_length = response.request.META['CONTENT_LENGTH']
            else:
                msg.request_content_length = None
        else:
            msg.request_content_length = None
        if 'SERVER_PROTOCOL' in response.request.META:
            server_protocol = response.request.META['SERVER_PROTOCOL']
            if server_protocol in PROTOCOL_CHOICES_LOOKUP:
                msg.protocol = PROTOCOL_CHOICES_LOOKUP[server_protocol]
            else:
                msg.protocol = UNKNOWN
        else:
            msg.protocol = UNKNOWN
        
        msg.status_code = response.status_code

        msg.cached = response.cached
        if 'content-encoding' in response:
            if response['content-encoding'] == 'deflate':
                msg.compress = DEFLATE
            elif response['content-encoding'] == 'gzip':
                msg.compress = GZIP
            else:
                msg.compress = UNCOMPRESSED
        else:
            msg.compress = UNCOMPRESSED
        
        msg.session_key = response.request.session.session_key
        if msg.session_key:
            user = response.request.session.get('_auth_user_id')
            if user:
                msg.user_id = int(user)
            else:
                msg.user_id = None
        else:
            msg.user_id = None
        msg.session_start_time = response.request.session.get('session_start_time')
        if response.__class__.__name__ == 'LoggingStreamingHTTPResponse':
            # lol race condition where we have to wait for cache populating
            # waiting 50 ms should be enough.
            # Should convert to Python 3.5+ async/await or a signaling framework,
            # but it's in another process.
#            if not msg.cached:
#                time.sleep(.05)
            cache_content = cache.get(response.pageKey)
            if cache_content == None:
                #doh! cache already expired before we could measure it.
#                msg.response_content_length = response.length
                msg.response_content_length = 0
            else:
                msg.response_content_length = len(cache_content)
        else:
            msg.response_content_length = response.length

        msg.response_content_type = msg.request_content_type
        
        msg.latitude = None
        msg.longitude = None

        return msg

    
    def log(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        self.write(self.cursor, self._lock, msg)

    def log_multiprocess(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        self.q.put(msg)
        self.e.set()

    def log_uwsgi(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        picklestring = pickle.dumps(msg)
        uwsgi.mule_msg(picklestring,1)

    if not uwsgi_mode:
        q = multiprocessing.Queue()
        e = multiprocessing.Event()
        @staticmethod
        def log_process_listener(e,q):
            cursor = connection.cursor().connection.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor)
            database_log = logging.getLogger("database")
            file_name = 'mozumder/include/sql/logging.sql'
            try:
                file = open(file_name, 'r')
            except FileNotFoundError:
                database_log.debug('No SQL file: %s' % file_name)
                pass
            except (OSError, IOError) as e:
                database_log.error('Error reading SQL file: %s' % file_name)
                raise e
            else:
                sql_commands=file.read().strip()
                if sql_commands:
                    try:
                        cursor.execute(sql_commands)
                    except psycopg2.errors.DuplicatePreparedStatement:
                        pass
            lock=threading.Lock()
            logwriter = LogWriter(
                cursor=cursor,
                lock=lock
            )
            while True:
                event_is_set = e.wait()
                msg = q.get()
                logwriter.threaded_write(msg)
                e.clear()


