from os.path import join, dirname
import base64
import hashlib
import zlib
import copy
import inspect

from django.apps import apps
from django.conf import settings
from django.db import connection
import psycopg2

import mozumder
from mozumder.views.zip import Zip

class Block():
    context_vary = False

    components = ()
    
    # 'vary' is used to select fields for cache keys
    vary = []
    # Each block doesn't hava a cache expiration time by default.
    cache_time = None

    # Each block has a permanently open cursor connection
    conn = connection.cursor().connection
    _lock = apps.get_app_config('mozumder')._lock

    inline_head_css = ''
    inline_head_js = ''
    inline_bodyopen_js = ''
    inline_bodyclose_js = ''
    
    def __init__(
        self,
        components=None,
        cache_key=None,
        cache_time=None,
        vary=None,
        inline_head_css=None,
        inline_head_js=None,
        inline_bodyopen_js=None,
        inline_bodyclose_js=None
        ):
        self.c = self.conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
        # Block defaults can be overridden through parameters passed here
        # during instatiation.
        if components:
            self.components = components
        if cache_key:
            self.cache_key = cache_key
        else:
            self.cache_key = self.__class__.__name__
        if cache_time:
            self.cache_time = cache_time
        if vary:
            self.vary = vary
        if inline_head_css:
            self.inline_head_css = inline_head_css
        if inline_head_js:
            self.inline_head_js = inline_head_js
        if inline_bodyopen_js:
            self.inline_bodyopen_js = inline_bodyopen_js
        if inline_head_css:
            self.inline_bodyclose_js = inline_bodyclose_js

    def generate_cache_key(self, context):
        key = f'{settings.PROJECT_NAME}:{self.cache_key}'
        for vary in self.vary:
            key = f'{key}:{context[vary]}'
        return key

    @staticmethod
    def read(filename,appdir=None):
        if settings.DEBUG:
            filepath = html_debug_dir + '/' + filename
        else:
            filepath = html_dir + '/' + filename
        if appdir:
            filepath = appdir + '/templates/' + filepath
        with open(filepath, 'r') as file:
            return file.read().rstrip('\n')

    def HTMLGenerator(self,context=None):
        for component in self.components:
            component.html.send()
            yield from component.html.send(context)

    def InlineHeadCSSGenerator(self,context=None):
        for component in self.components:
            component.inline_head_css.send()
            yield from component.inline_head_css.send(context)

    def InlineHeadJSGenerator(self,context=None):
        for component in self.components:
            component.inline_head_js.send()
            yield from component.inline_head_js.send(context)

    def InlineBodyOpenGenerator(self,context=None):
        for component in self.components:
            component.inline_bodyopen_js.send()
            yield from component.inline_bodyopen_js.send(context)

    def InlineBodyCloseGenerator(self,context=None):
        for component in self.components:
            component.inline_bodyclose_js.send()
            yield from component.inline_bodyclose_js.send(context)

    def generate_html(self,context=None):
        if self.components:
            html = ''
            for i in self.HTMLGenerator(context):
                html = html + i
            return html
        else:
            return self.html
    def generate_inline_head_css(self,context=None):
        if self.components:
            css = ''
            for i in self.InlineHeadCSSGenerator(context):
                css = css + ' ' + i
            return css
        else:
            return self.inline_head_css
    def generate_inline_head_js(self,context=None):
        if self.components:
            js = ''
            for i in self.InlineHeadJSGenerator(context):
                js = js + i
            return js
        else:
            return self.inline_head_js
    def generate_inline_bodyopen_js(self,context=None):
        if self.components:
            openjs = ''
            for i in self.InlineBodyOpenGenerator(context):
                openjs = openjs + i
            return openjs
        else:
            return self.inline_bodyopen_js
    def generate_inline_bodyclose_js(self,context=None):
        if self.components:
            closejs = ''
            for i in self.InlineBodyCloseGenerator(context):
                closejs = closejs + i
            return closejs
        else:
            return self.inline_bodyclose_js

    def fetchall(self):
        with self._lock:
            self.c.execute('EXECUTE ' + self.sql + ';')
            result = self.c.fetchall()
        return result


def csphash(text):
    return str(
        base64.b64encode(
            hashlib.sha256(
                bytes(text,'utf-8')
            ).digest()),
        'utf-8')

class MozumderTemplate(Zip):

    """
    Each Template instance has its own Compressor object, its own Content-security
    policy, and its own set of blocks to include.
    """

    base_dir = dirname(inspect.getfile(mozumder))

    include_dir = join(base_dir, 'include')
    src_dir = join(include_dir, 'src')
    lib_dir = join(include_dir, 'lib')
    html_dir = join(lib_dir, 'html')
    js_dir = join(lib_dir, 'js')
    js_fragments_dir = join(js_dir, 'fragments')
    css_dir = join(lib_dir, 'css')
    html_debug_dir = join(src_dir, 'html')
    js_debug_dir = join(src_dir, 'js')
    js_fragments_debug_dir = join(js_debug_dir, 'fragments')
    css_debug_dir = join(src_dir, 'css')

    html_headers_include = ''
    inline_head_css_include = ''
    inline_head_js_include = ''
    inline_bodyopen_js_include = ''
    inline_bodyclose_js_include = ''

    def generate_inline_head_css(self):
        if self.blocks:
            css = ''
            for block in self.blocks:
                addcss = block.generate_inline_head_css(self)
                css = css + ' ' + addcss
            return css
        else:
            return self.inline_head_css
    def generate_inline_head_js(self):
        if self.blocks:
            js = ''
            for block in self.blocks:
                js = js + block.generate_inline_head_js(self)
            return js
        else:
            return self.inline_head_js

    def generate_inline_bodyopen_js(self):
        if self.blocks:
            js = ''
            for block in self.blocks:
                js = js + block.generate_inline_bodyopen_js(self)
            return js
        else:
            return self.inline_bodyopen_js

    def generate_inline_bodyclose_js(self):
        if self.blocks:
            js = ''
            for block in self.blocks:
                js = js + block.generate_inline_bodyclose_js(self)
            return js
        else:
            return self.inline_bodyclose_js

    generate_csp = True
    
    def __init__(self):
        """
        On startup, each template goes through all the components to collect
        all the Javascript and CSS, calculates Content-Security-Protocol hashes,
        and starts the Zlib compressor with precalculated HTML opening and
        closing compression blocks.
        """

        inline_head_css = self.generate_inline_head_css()
        inline_head_js = self.generate_inline_head_js()
        inline_bodyopen_js = self.generate_inline_bodyopen_js()
        inline_bodyclose_js = self.generate_inline_bodyopen_js()
        html_headers = ''

        if settings.DEBUG:
            inline_head_css_include = join(
                self.css_debug_dir,
                self.inline_head_css_include)
            inline_head_js_include = join(
                self.js_debug_dir,
                self.inline_head_js_include)
            inline_bodyopen_js_include = join(
                self.js_fragments_debug_dir,
                self.inline_bodyopen_js_include)
            inline_bodyclose_js_include = join(
                self.js_fragments_debug_dir,
                self.inline_bodyclose_js_include)
            html_headers_include = join(
                self.html_debug_dir,
                self.html_headers_include)
        else:
            inline_head_css_include = join(
                self.css_dir,
                self.inline_head_css_include)
            inline_head_js_include = join(
                self.js_dir,
                self.inline_head_js_include)
            inline_bodyopen_js_include = join(
                self.js_fragments_dir,
                self.inline_bodyopen_js_include)
            inline_bodyclose_js_include = join(
                self.js_fragments_dir,
                self.inline_bodyclose_js_include)
            html_headers_include = join(
                self.html_dir,
                self.html_headers_include)

        if self.inline_head_css_include:
            with open(inline_head_css_include, 'r') as \
                inline_head_css_include_file:
                inline_head_css += \
                    inline_head_css_include_file.read().rstrip('\n')
        if self.inline_head_js_include:
            with open(inline_head_js_include, 'r') as \
                inline_head_js_include_file:
                inline_head_js += \
                    inline_head_js_include_file.read().rstrip('\n')
        if self.inline_bodyopen_js_include:
            with open(inline_bodyopen_js_include, 'r') as \
                inline_bodyopen_js_include_file:
                inline_bodyopen_js += \
                    inline_bodyopen_js_include_file.read().rstrip('\n')
        if self.inline_bodyclose_js_include:
            with open(inline_bodyclose_js_include, 'r') as \
                inline_bodyclose_js_include_file:
                inline_bodyclose_js += \
                    inline_bodyclose_js_include_file.read().rstrip('\n')
        if self.html_headers_include:
            with open(html_headers_include, 'r') as html_headers_include_file:
                html_headers += html_headers_include_file.read().rstrip('\n')

        base_csp = copy.deepcopy(getattr(settings, "BASE_CSP", {}))
                    
        if inline_head_css:
            if 'style-src' not in base_csp:
                base_csp['style-src'] = []
            hash=csphash(inline_head_css)
            base_csp['style-src'].append(f"'sha256-{hash}'")
            html_headers = html_headers + '<style>' + inline_head_css + '</style>'

        if inline_head_js or inline_bodyopen_js or inline_bodyclose_js:
            if 'script-src' not in base_csp:
                base_csp['script-src'] = []
        if inline_head_js:
            hash = csphash(inline_head_js)
            base_csp['script-src'].append(f"'sha256-{hash}'")
            html_headers = html_headers + '<script>' + inline_head_js + '</script>'
        if inline_bodyopen_js:
            hash = csphash(inline_bodyopen_js)
            base_csp['script-src'].append(f"'sha256-{hash}'")
        if inline_bodyclose_js:
            hash = csphash(inline_bodyclose_js)
            base_csp['script-src'].append(f"'sha256-{hash}'")
        self.csp = " ; ".join([key + " " + " ".join(values) for key, values in base_csp.items()])
        
        del base_csp

        try:
            analytics = settings.ANALYTICS
        except:
            analytics = False

        # Save inline_bodyopen_js in instance for block use.
        if inline_bodyopen_js:
            self.body_opening = '<script type="text/javascript">' + inline_bodyopen_js + '</script>'
        else:
            self.body_opening = ''

        if inline_bodyclose_js:
            body_closing = '<script>' + inline_bodyclose_js + '</script><noscript><div class="off"></div></noscript></div></body></html>'
        else:
            body_closing = '</div></body></html>'


        startCompressor = zlib.compressobj(level=self.level, wbits=self.wbits)
        hStart = bytes(html_headers,'utf-8')
        hEnd = bytes(body_closing,'utf-8')
        zStart = startCompressor.compress(hStart)
        zStart += startCompressor.flush(zlib.Z_FULL_FLUSH)
        zEnd = startCompressor.compress(hEnd)
        zEnd += startCompressor.flush(zlib.Z_FINISH)
        self.zStart = zStart
        self.zEnd = zEnd

