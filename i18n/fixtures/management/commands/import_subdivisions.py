from django.core.management.base import BaseCommand, CommandError
from datetime import date
from datapackage import Package
import pycountry
import gettext
from os import listdir
import logging

from i18n.models import Country, CountryLang, Subdivision, SubdivisionLang, SubdivisionType, SubdivisionTypeLang, Language, Lang

logger = logging.getLogger("management")

class Command(BaseCommand):

    help = 'Imports ISO 3166 Country Codes'

    def add_arguments(self, parser):

        parser.add_argument(
            '-l', '--locale_dir',
            action='store',
            dest='locales_dir',
            default=pycountry.LOCALES_DIR,
            help="Locale Dir",
        )
        parser.add_argument(
            '-lang_en', '--default_english_lang',
            action='store',
            dest='default_en_lang',
            default="en",
            help="ISO 693-1 code for default English language if not 'en'.",
        )

    def handle(self, *args, **options):

        en_language = Language.objects.get(iso_639_1=options['default_en_lang'])
        en_lang = Lang.objects.get(language=en_language, script=None, country=None, variant=None, extension=None, private_use=None)

        logger.debug(f"{options['locales_dir']=}")
        files = listdir(options['locales_dir'])

        data = list(pycountry.subdivisions)
        total = 0
        subdivisions = []
        children = []
        for row in data:
            subdivision_code = row.code
            subdivision_name = row.name
            type_name = row.type
            country_name = row.country_code
            country = Country.objects.get(alpha_2=country_name)

            subdivision_type_lang = SubdivisionTypeLang.objects.filter(
                name=type_name,
                lang=en_lang
                )
            if len(subdivision_type_lang) == 0:
                subdivision_type = SubdivisionType.objects.create()
                SubdivisionTypeLang.objects.create(
                    type=subdivision_type,
                    name=type_name,
                    lang=en_lang
                )
                logger.debug(f'created new subdivision type: {type_name}')
            else:
                subdivision_type = SubdivisionType.objects.get(
                    id=subdivision_type_lang[0].type.id
                )

            subdivision, subdivision_created = Subdivision.objects.get_or_create(
                code=subdivision_code.split('-')[1],
                type=subdivision_type,
                country=country,
                parent=None
                )
            subdivisions.append(subdivision)
            if row.parent_code != None:
                children.append(row)
            subdivision_lang, subdivision_lang_created = SubdivisionLang.objects.get_or_create(
                subdivision=subdivision,
                name=subdivision_name,
                lang=en_lang,
            )
            total += 1
        # Save
        Subdivision.objects.bulk_update(subdivisions, [
            'code',
            'type',
            'country',
            ], batch_size=50)
        logger.info(f'   -- Initialized {total} subdivision')
        logger.info(f'   -- Found {len(children)} children subdivisions')
        
        total=0
        subdivisions = []
        for row in children:
            subdivision_code = row.code
            subdivision_name = row.name
            type_name = row.type
            country_name = row.country_code
            country = Country.objects.get(alpha_2=country_name)

            subdivision_type_lang = SubdivisionTypeLang.objects.get(
                name=type_name,
                lang=en_lang
                )
            subdivision_type = SubdivisionType.objects.get(
                id=subdivision_type_lang.type.id
            )

            parent_code = row.parent_code.split('-')[-1]
            parent_subdivision = Subdivision.objects.get(
                code=parent_code,
                country=country
            )

            subdivision = Subdivision.objects.get(
                code=subdivision_code.split('-')[1],
                type=subdivision_type,
                country=country
                )
            subdivision.parent = parent_subdivision
            subdivisions.append(subdivision)
            total += 1
        Subdivision.objects.bulk_update(subdivisions, [
            'parent'
            ], batch_size=50)
        logger.info(f'   -- Updated {total} children subdivisions')

        total = 0
        for language_code in files:
            subdivision_langs = []
            logger.debug(f"Translating Locale: {language_code}")
            try:
                translate_language = gettext.translation('iso3166-2', locales_dir, languages=[language_code])
            except:
                logger.warning(f"Can't find country translation for: {language_code}")
                continue
            translate_language.install()
            variant_subtags = language_code.split('@')
            if len(variant_subtags) == 2:
                variant = variant_subtags[1]
                logger.debug(f"Variant: {variant}")
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
                logger.debug(f"Country: {subtags[1]}")
            else:
                country = None
            lang = Lang.objects.get(language=language, script=None, country=country, variant=variant)
                        
            subtotal = 0
            for row in data:
                subdivision_code = row.code.split('-')[-1]
                subdivision_name = row.name
                subdivision_country_name = row.country_code
                subdivision_country = Country.objects.get(alpha_2=subdivision_country_name)

                subdivision = Subdivision.objects.get(
                    code=subdivision_code,
                    country=subdivision_country,
                )
                subdivision_lang, subdivision_lang_created = SubdivisionLang.objects.get_or_create(
                    subdivision=subdivision,
                    lang=lang,
                )
                try:
                    translated_name =  translate_language.gettext(subdivision_name)
                except:
                    logger.warning(f"  -- couldn't translate: {subdivision_name}")
                    continue
                subdivision_lang.name = translated_name

                subdivision_langs.append(subdivision_lang)
                total += 1
                subtotal += 1
            logger.info(f'  -- Found {subtotal} translations for {language_code}')
            SubdivisionLang.objects.bulk_update(subdivision_langs, [
                'subdivision',
                'name',
                'lang',
                ], batch_size=50)

        logger.info(f'-- Updated {total} subdivision translations')
        return
