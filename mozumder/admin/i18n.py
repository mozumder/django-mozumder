from django.contrib import admin

from ..models import Language, LanguageLang, RetiredLanguage, \
    MacroLanguageMapping, Script, ScriptLang, Country, CountryLang, \
    Subdivision, SubdivisionLang, SubdivisionType, SubdivisionTypeLang, Lang, \
    LangLang, Locale, LocaleLang

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'iso_639_3', 'iso_639_1', 'iso_639_2b', 'iso_639_2t', 'scope', 'type')
    list_display_links = ('id',)
    list_editable = ('iso_639_3', 'iso_639_1', 'iso_639_2b', 'iso_639_2t', 'scope', 'type')
    search_fields = ['iso_639_3', 'iso_639_1', 'iso_639_2b', 'iso_639_2t']
admin.site.register(Language, LanguageAdmin)

class LanguageLangAdmin(admin.ModelAdmin):
    list_display = ('id', 'lang', 'language', 'ref_name', 'print_name', 'inverted_name')
    list_display_links = ('language',)
    list_editable = ('ref_name', 'print_name', 'inverted_name')
    search_fields = ['print_name','inverted_name', 'language__iso_639_3', 'language__iso_639_2b', 'language__iso_639_2t','language__iso_639_1']
admin.site.register(LanguageLang, LanguageLangAdmin)

class RetiredLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'iso_639_3', 'ref_name', 'reason', 'change_to', 'ret_remedy', 'effective_date')
    list_display_links = ('id',)
    list_editable = ('iso_639_3', 'ref_name', 'reason', 'change_to', 'ret_remedy', 'effective_date')
    search_fields = ['iso_639_3', 'ref_name', 'change_to', 'ret_remedy']
admin.site.register(RetiredLanguage,RetiredLanguageAdmin)

class MacroLanguageMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'macrolanguage', 'status', 'individual_language', 'retired_individual_language')
    list_display_links = ('id',)
    raw_id_fields = ['macrolanguage', 'individual_language', 'retired_individual_language']
    list_editable = ['status',]
    search_fields = ['macrolanguage', 'status', 'individual_language', 'retired_individual_language']
admin.site.register(MacroLanguageMapping, MacroLanguageMappingAdmin)

class ScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'iso_15294', 'code_number', 'unicode_alias','unicode_version', 'version_date')
    list_display_links = ('iso_15294',)
    list_editable = ('code_number', 'unicode_alias','unicode_version', 'version_date')
admin.site.register(Script, ScriptAdmin)

class ScriptLangAdmin(admin.ModelAdmin):
    list_display = ('id', 'lang', 'script', 'name')
    list_display_links = ('script',)
    list_editable = ('name',)
admin.site.register(ScriptLang, ScriptLangAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'alpha_2', 'alpha_3', 'numeric')
    list_display_links = ('id',)
admin.site.register(Country, CountryAdmin)

class CountryLangAdmin(admin.ModelAdmin):
    list_display = ('id', 'lang', 'country', 'name', 'official_name', 'common_name', 'UN_formal_name', 'UN_short_name')
    list_display_links = ('country',)
    list_editable = ('official_name', 'UN_formal_name', 'UN_short_name',)
admin.site.register(CountryLang, CountryLangAdmin)


class SubdivisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'country', 'parent', 'type')
    list_display_links = ('id',)
    search_fields = ['code', 'country__alpha_2']
admin.site.register(Subdivision, SubdivisionAdmin)

class SubdivisionLangAdmin(admin.ModelAdmin):
    list_display = ('id', 'lang', 'subdivision', 'name')
    list_display_links = ('subdivision',)
    search_fields = ['name','subdivision__code', ]
admin.site.register(SubdivisionLang, SubdivisionLangAdmin)


class LangAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'script', 'country')
    list_display_links = ('id',)
    raw_id_fields = ['language', 'script', 'country']
    list_editable = ['language', 'script', 'country',]
admin.site.register(Lang, LangAdmin)

class LangLangAdmin(admin.ModelAdmin):
    list_display = ('id','lang', 'namedlang','name')
    list_display_links = ('id',)
    list_editable = ('name',)
admin.site.register(LangLang, LangLangAdmin)


class LocaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'script', 'country')
    list_display_links = ('id',)
    list_editable = ('language', 'script', 'country',)
admin.site.register(Locale, LocaleAdmin)

class LocaleLangAdmin(admin.ModelAdmin):
    list_display = ('id','lang', 'locale', 'name')
    list_display_links = ('id',)
    list_editable = ('name',)
admin.site.register(LocaleLang, LocaleLangAdmin)
