from django.core.management.base import BaseCommand, CommandError
from datetime import date
from datapackage import Package
import pycountry
import gettext
from os import listdir
import logging

from i18n.models import Country, CountryLang, Language, Lang

logger = logging.getLogger("management")

class Command(BaseCommand):

    help = 'Imports ISO 3166 Country Codes'

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--codes_url',
            action='store',
            dest='codes_url',
            default='https://datahub.io/core/country-codes/datapackage.json',
            help="Codes URL",
        )
        parser.add_argument(
            '-l', '--locale_dir',
            action='store',
            dest='locale_dir',
            default='/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/django_countries/locale/',
            help="Locale Dir",
        )
        parser.add_argument(
            '-lang_en', '--default_english_lang',
            action='store',
            dest='default_en_lang',
            default="en",
            help="ISO 693-1 code for default English language if not 'en'.",
        )
        parser.add_argument(
            '-lang_fr', '--default_french_lang',
            action='store',
            dest='default_fr_lang',
            default="fr",
            help="ISO 693-1 code for default French language if not 'fr'.",
        )
        parser.add_argument(
            '-lang_es', '--default_spanish_lang',
            action='store',
            dest='default_es_lang',
            default="es",
            help="ISO 693-1 code for default Spanish language if not 'es'.",
        )
        parser.add_argument(
            '-lang_it', '--default_italian_lang',
            action='store',
            dest='default_it_lang',
            default="it",
            help="ISO 693-1 code for default Italian language if not 'it'.",
        )
        parser.add_argument(
            '-lang_zh', '--default_chinese_lang',
            action='store',
            dest='default_zh_lang',
            default="zh",
            help="ISO 693-1 code for default Chinese language if not 'zh'.",
        )
        parser.add_argument(
            '-lang_ar', '--default_arabic_lang',
            action='store',
            dest='default_ar_lang',
            default="ar",
            help="ISO 693-1 code for default Arabic language if not 'ar'.",
        )
        parser.add_argument(
            '-lang_ru', '--default_russian_lang',
            action='store',
            dest='default_ru_lang',
            default="ru",
            help="ISO 693-1 code for default Russian language if not 'ru'.",
        )

    def handle(self, *args, **options):

        language_codes = [
            options['default_en_lang'],
            options['default_es_lang'],
            options['default_fr_lang'],
            options['default_it_lang'],
            options['default_zh_lang'],
            options['default_ar_lang'],
            options['default_ru_lang'],
            ]
        for language_code in language_codes:
            language = Language.objects.get(iso_639_1=language_code)
            # Check for multiple languages
            lang, lang_created = Lang.objects.get_or_create(
                language=language,
                country__isnull=True,
                script__isnull=True)
            lang.active = True
            if lang_created:
                lang.save()
                logger.info(f' -- Actived default language: {lang}' )

        data = list(pycountry.countries)
        total = 0
        countries = []
        for row in data:
            total += 1
            country, country_created = Country.objects.get_or_create(
                alpha_2=row.alpha_2,
                alpha_3=row.alpha_3,
                numeric=row.numeric,
                )
            countries.append(country)
        # Save
        Country.objects.bulk_update(countries, [
            'alpha_2',
            'alpha_3',
            'numeric',
            ], batch_size=50)
        logger.info(f' -- Initialized {total} countries')

        en_language = Language.objects.get(iso_639_1=options['default_en_lang'])
        en_lang = Lang.objects.get(language=en_language, script=None, country=None, variant=None, extension=None, private_use=None)
        total = 0
        country_langs = []
        for row in data:
            total += 1
            country = Country.objects.get(alpha_3=row.alpha_3)
            country_lang, country_lang_created = CountryLang.objects.get_or_create(
                country=country,
                lang=en_lang)
            country_lang.name = row.name
            if hasattr(row, 'official_name'):
                country_lang.official_name = row.official_name
            if hasattr(row, 'common_name'):
                country_lang.common_name = row.common_name
            country_langs.append(country_lang)
        CountryLang.objects.bulk_update(country_langs, [
            'country',
            'lang',
            'name',
            'official_name',
            'common_name',
            ], batch_size=20)
        logger.info(f' -- Initialized {total} country langs')

        locales_dir = pycountry.LOCALES_DIR
        logger.debug(f'{locales_dir=}')
        files = listdir(locales_dir)
        logger.debug(f'All Locales: {files}')

        translations = []

        for language_code in files:
            logger.debug(f'Locale: {language_code}')
            try:
                translate_language = gettext.translation('iso3166-1', locales_dir, languages=[language_code])
            except:
                logger.error(f"Can't find country translation for: {language_code}")
                continue
            translate_language.install()
            variant_subtags = language_code.split('@')
            if len(variant_subtags) == 2:
                variant = variant_subtags[1]
                logger.debug(f'Variant: {variant}')
            else:
                variant = None
            subtags = variant_subtags[0].split('_')
            try:
                if len(subtags[0]) == 2:
                    language = Language.objects.get(iso_639_1=subtags[0])
                else:
                    language = Language.objects.get(iso_639_3=subtags[0])
            except:
                continue
            if len(subtags) == 2:
                if len(subtags[0]) == 2:
                    country = Country.objects.get(alpha_2=subtags[1])
                else:
                    country = Country.objects.get(alpha_3=subtags[1])
                logger.debug(f'Country: {subtags[1]}')
            else:
                country = None
            lang, lang_created = Lang.objects.get_or_create(language=language, script=None, country=country, variant=variant)
            lang.save()
            for country in Country.objects.all():
                country_en_lang = CountryLang.objects.get(country=country, lang=en_lang)
                country_en_name = country_en_lang.name
                country_lang, country_lang_created = CountryLang.objects.get_or_create(country=country, lang=lang)
                country_lang.name = _(country_en_name)
                country_lang.save()
                translations.append(country_lang)
        CountryLang.objects.bulk_update(translations, [
            'country',
            'lang',
            'name',
            'official_name',
            'common_name',
            ], batch_size=50)

        return

        package = Package(options['codes_url'])
        data = package.get_resource('country-codes').read(keyed=True)

        total = 0
        countries = []
        for row in data:
            total += 1
            alpha_2 = row['ISO3166-1-Alpha-2']
            if alpha_2 == None:
                continue
            alpha_3 = row['ISO3166-1-Alpha-3']
            if alpha_3 == None:
                continue
            numeric = row['ISO3166-1-numeric']
            if numeric == None:
                continue
            country, country_created = Country.objects.get_or_create(
                alpha_2=alpha_2,
                alpha_3=alpha_3,
                numeric=numeric,
                )
            countrys.append(country)
        # Save
        Country.objects.bulk_update(countrys, [
            'alpha_2',
            'alpha_3',
            'numeric',
            ], batch_size=50)
        logger.info(f' -- Initialized {total} countries')

        total = 0
        country_langs = []
        for row in data:
            total += 1
            alpha_3 = row['ISO3166-1-Alpha-3']
            if alpha_3 == None:
                continue
            country = Country.objects.get(alpha_3=alpha_3)
            for language_code in language_codes:
                language = Language.objects.get(iso_639_1=language_code)
                lang = Lang.objects.get(language=language)
                # Check for multiple languages
                if language_code == "en":
                    official_name = row['official_name_en']
                    UN_formal_name = row['UNTERM English Formal']
                    UN_short_name = row['UNTERM English Short']
                if language_code == "es":
                    official_name = row['official_name_es']
                    UN_formal_name = row['UNTERM Spanish Formal']
                    UN_short_name = row['UNTERM Spanish Short']
                if language_code == "fr":
                    official_name = row['official_name_fr']
                    UN_formal_name = row['UNTERM French Formal']
                    UN_short_name = row['UNTERM French Short']
                if language_code == "it":
                    official_name = row['official_name_it']
                    UN_formal_name = row['UNTERM Italian Formal']
                    UN_short_name = row['UNTERM Italian Short']
                if language_code == "zh":
                    official_name = row['official_name_cn']
                    UN_formal_name = row['UNTERM Chinese Formal']
                    UN_short_name = row['UNTERM Chinese Short']
                if language_code == "ar":
                    official_name = row['official_name_ar']
                    UN_formal_name = row['UNTERM Arabic Formal']
                    UN_short_name = row['UNTERM Arabic Short']
                if language_code == "ru":
                    official_name = row['official_name_ru']
                    UN_formal_name = row['UNTERM Russian Formal']
                    UN_short_name = row['UNTERM Russian Short']
                if official_name == None:
                    logger.debug(f'{country=}')
                    logger.debug(f'{lang=}')
                    logger.debug(f'{official_name=}')
                    logger.debug(f'{UN_formal_name=}')
                    logger.debug(f'{UN_short_name=}')
                    continue

                country_lang, country_lang_created = CountryLang.objects.get_or_create(
                    country=country,
                    lang=lang)
                country_lang.official_name = official_name
                country_lang.UN_formal_name = UN_formal_name
                country_lang.UN_short_name = UN_short_name
                country_langs.append(country_lang)
        CountryLang.objects.bulk_update(country_langs, [
            'country',
            'lang',
            'official_name',
            'UN_formal_name',
            'UN_short_name',
            ], batch_size=20)
        logger.info(f' -- Initialized {total} country langs')
