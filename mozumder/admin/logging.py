from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from ..models import Domain, HostName, IP, Path, QueryString, URL, MIME, \
    Accept, LanguageCode, Encoding, Browser, OS, Device, UserAgent, SessionLog, \
    AccessLogManager, AccessLog

@admin.register(IP)
class IPAdmin(admin.ModelAdmin):
    list_display = ['id', 'address','bot','latitude','longitude',]
    list_display_links = ['id',]
    list_editable = ['bot',]
    list_filter = ('bot',)
    readonly_fields=('id',)
    search_fields = ['address']
    fieldsets = [
        (None, {'fields': [
            ('address'),
            ('bot'),
            ]
        }),
        ('Geolocation', {'fields': [
            ('latitude'),
            ('longitude'),
            ]
        }),
    ]

@admin.register(HostName)
class HostNameAdmin(admin.ModelAdmin):
    def domain_link(self, obj):
        if obj.domain:
            url = reverse('admin:analytics_domain_change', args = [obj.domain.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.domain.__str__())
        else:
            html = format_html("-")
        return html
    list_display = ['id', 'name','domain_link', 'date_updated']
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('date_updated'),
            ]
        }),
    ]

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot', 'name', 'date_updated']
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('bot'),
            ('date_updated'),
            ]
        }),
    ]

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ['id', 'search_path',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['search_path']
    fieldsets = [
        (None, {'fields': [
            ('search_path'),
            ]
        }),
    ]

@admin.register(QueryString)
class QueryStringAdmin(admin.ModelAdmin):
    list_display = ['id', 'query_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['query_string']
    fieldsets = [
        (None, {'fields': [
            ('query_string'),
            ]
        }),
    ]

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ['id','name','canonical','scheme','authority','port','path','query_string']
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['name','canonical',]
    list_filter = ('scheme','authority','port','path','query_string')
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('canonical'),
            ]
        }),
        ('Parts', {'fields': [
            ('scheme'),
            ('authority'),
            ('port'),
            ('path'),
            ('query_string'),
            ]
        }),
    ]

@admin.register(MIME)
class MIMEAdmin(admin.ModelAdmin):
    list_display = ['id', 'mime_type_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['mime_type_string']
    fieldsets = [
        (None, {'fields': [
            ('mime_type_string'),
            ]
        }),
    ]

@admin.register(Accept)
class AcceptAdmin(admin.ModelAdmin):
    list_display = ['id', 'accept_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['accept_string']
    fieldsets = [
        (None, {'fields': [
            ('accept_string'),
            ]
        }),
    ]

@admin.register(LanguageCode)
class LanguageCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'language_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['language_string']
    fieldsets = [
        (None, {'fields': [
            ('language_string'),
            ]
        }),
    ]

@admin.register(Encoding)
class EncodingAdmin(admin.ModelAdmin):
    list_display = ['id', 'encoding_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['encoding_string']
    fieldsets = [
        (None, {'fields': [
            ('encoding_string'),
            ]
        }),
    ]

@admin.register(Browser)
class BrowserAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'major_version', 'minor_version',]
    list_display_links = ['id','family', 'major_version', 'minor_version',]
    readonly_fields=('id',)
    search_fields = ['family']
    list_filter = ('family','major_version',)
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('major_version', 'minor_version',),
            ('patch',),
            ]
        }),
    ]

@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'major_version', 'minor_version',]
    list_display_links = ['id','family', 'major_version', 'minor_version',]
    readonly_fields=('id',)
    search_fields = ['family']
    list_filter = ('family','major_version',)
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('major_version', 'minor_version',),
            ('patch','minor_patch'),
            ]
        }),
    ]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot', 'family', 'brand', 'model','mobile','pc','tablet','touch']
    list_display_links = ['id','family', 'brand', 'model',]
    readonly_fields=('id',)
    search_fields = ['family', 'brand', 'model',]
    list_filter = ('family','brand','model','mobile','pc','tablet','touch')
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('brand', 'model',),
            ('mobile','pc','tablet','touch',),
            ('bot',),
            ]
        }),
    ]

@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot', 'browser_link', 'os_link', 'device_link', 'user_agent_string',]
    def browser_link(self, obj):
        if obj.browser:
            url = reverse('admin:analytics_browser_change', args = [obj.browser.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.browser.__str__())
        else:
            html = format_html("-")
        return html
    browser_link.admin_order_field = 'Browser'
    browser_link.short_description = 'Browser'
    def os_link(self, obj):
        if obj.os:
            url = reverse('admin:analytics_os_change', args = [obj.os.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.os.__str__())
        else:
            html = format_html("-")
        return html
    os_link.admin_order_field = 'OS'
    os_link.short_description = 'Operating System'
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:analytics_device_change', args = [obj.device.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.device.__str__())
        else:
            html = format_html("-")
        return html
    device_link.admin_order_field = 'Device'
    device_link.short_description = 'Device'
    list_display_links = ['id','browser_link', 'os_link', 'device_link', ]
    list_editable = ['bot',]
    list_filter = ('bot','browser','os', 'device',)
    readonly_fields=('id',)
    search_fields = ['user_agent_string']
    fieldsets = [
        (None, {'fields': [
            ('user_agent_string'),
            ('bot'),
            ('browser',),
            ('os',),
            ('device'),
            ]
        }),
    ]

@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot','user_id','start_time','expire_time','session_key',]
    list_display_links = ['id',]
    list_editable = ['bot',]
    list_filter = ('bot','user_id','start_time','expire_time')
    readonly_fields=('id',)
    search_fields = ['user_id']
    fieldsets = [
        (None, {'fields': [
            ('session_key'),
            ('bot'),
            ('user_id'),
            ]
        }),
        ('Time', {'fields': [
            ('start_time'),
            ('expire_time'),
            ]
        }),
    ]

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    def ip_link(self, obj):
        if obj.ip:
            url = reverse('admin:analytics_ip_change', args = [obj.ip.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.ip.__str__())
        else:
            html = format_html("-")
        return html
    ip_link.admin_order_field = 'IP'
    ip_link.short_description = 'IP'
    def domain_link(self, obj):
        if obj.ip.host:
            url = reverse('admin:analytics_hostname_change', args = [obj.ip.host.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.ip.host.domain_name())
        else:
            html = format_html("-")
        return html
    domain_link.admin_order_field = 'Domain'
    domain_link.short_description = 'Domain'
    def ua_link(self, obj):
        if obj.user_agent:
            url = reverse('admin:analytics_useragent_change', args = [obj.user_agent.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.user_agent.__str__())
        else:
            html = format_html("-")
        return html
    ua_link.admin_order_field = 'User Agent'
    ua_link.short_description = 'User Agent'
    def request_url_link(self, obj):
        if obj.status in [401,402,403,500]:
            color = RED
        elif obj.status in [404]:
            color = ORANGE
        elif obj.status in [410]:
            color = PURPLE
        elif obj.status in [301,302,308,309]:
            color = BLUE
        elif obj.ajax:
            color = GRAY
        else:
            color = BLACK
        if obj.request_url:
            url = reverse('admin:analytics_url_change', args = [obj.request_url.id])
            html = format_html("<span style='color: {};'><a href='{}'>{}</a></span>", color, url, obj.request_url.__str__()[:40])
        else:
            html = format_html("-")
        return html
    request_url_link.admin_order_field = 'Request URL'
    request_url_link.short_description = 'Request URL'
    def direction_link(self, obj):
        if obj.method:
            if METHOD_CHOICES_DICT[obj.method] == 'GET':
                method = '-'
            elif METHOD_CHOICES_DICT[obj.method] == 'POST':
                method = '+'
            else:
                method = '?'
        else:
            method = '*'
        if obj.ajax:
            direction = f'<{method}'
        else:
            direction = f'{method}>'
        return format_html(direction)
    direction_link.admin_order_field = ''
    direction_link.short_description = ''
    def referer_url_link(self, obj):
        if obj.referer_url:
            url = reverse('admin:analytics_url_change', args = [obj.referer_url.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.referer_url.__str__()[:40])
        else:
            html = format_html("*")
        return html
    referer_url_link.admin_order_field = 'Referer URL'
    referer_url_link.short_description = 'Referer URL'

    list_display = [
        'timestamp',
        'ip_link',
        'domain_link',
        'colored_response_time',
        'colored_size',
        'referer_url_link',
        'direction_link',
        'request_url_link',
        'ua_link']
    list_display_links = ['timestamp',]
    readonly_fields=(
        'timestamp',
        'user',
        'ip',
        'protocol',
        'request_url',
        'status',
        'method',
        'ajax',
        'preview',
        'prefetch',
        'lookup_time',
        'ssl_time',
        'connect_time',
        'response_time',
        'cached',
        'log_timestamp',
        'referer_url',
        'user_agent',
        'accept_type',
        'accept_language',
        'accept_encoding',
        'response_content_type',
        'response_content_length',
        'compress',
        'session',
        'session_log',
        'latitude',
        'longitude'
    )
    search_fields = [
        'timestamp',
        'ip__address',
        'request_url__name',
        'status',
        'user_agent__user_agent_string',
        'referer_url__name']
    fieldsets = [
        (None, {'fields': [
            ('timestamp','user'),
            ]
        }),
        ('Request', {'fields': [
            ('ip'),
            ('referer_url'),
            ('ajax'),
            ('preview'),
            ('prefetch'),
            ('user_agent'),
            ('accept_type'),
            ('accept_language'),
            ('accept_encoding'),
            ]
        }),
        ('URL', {'fields': [
            ('method'),
            ('request_url'),
            ('status'),
            ('protocol'),
            ]
        }),
        ('Response', {'fields': [
            ('response_content_type'),
            ('response_content_length'),
            ('compress'),
            ]
        }),
        ('Performance', {'fields': [
            ('lookup_time','ssl_time','connect_time'),
            ('response_time'),
            ('cached'),
            ('log_timestamp'),
            ]
        }),
        ('Session', {'fields': [
            ('session'),
            ('session_log'),
            ]
        }),
        ('Geolocation', {'fields': [
            ('latitude'),
            ('longitude'),
            ]
        }),
    ]
