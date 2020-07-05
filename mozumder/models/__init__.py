from .logging import Domain, HostName, IP, Path, QueryString, URL, MIME, \
    Accept, LanguageCode, Encoding, Browser, OS, Device, UserAgent, \
    SessionLog, AccessLogManager, AccessLog
from .i18n import Language, LanguageLang, RetiredLanguage, \
    MacroLanguageMapping, Script, ScriptLang, Country, CountryLang, \
    Subdivision, SubdivisionLang, SubdivisionType, SubdivisionTypeLang, Lang, \
    LangLang, Locale, LocaleLang

from .development import *

from django.utils.text import slugify as django_slugify

def slugify(text):
    return django_slugify(text.replace(" & ", " and ").replace(" + ", " and "))
