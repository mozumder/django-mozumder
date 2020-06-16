from django.core.management.base import BaseCommand, CommandError
from datetime import date
import logging
logger = logging.getLogger("management")

from i18n.models import Script, ScriptLang, Language, Lang

class Command(BaseCommand):

    help = 'Imports ISO 15294 Script codes from semicolon-delimited file'

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--codes_file',
            action='store',
            dest='codes_file',
            default='i18n/fixtures/iso15924-utf8-20190819.txt',
            help="""
Format:
    Code;N°;English Name;Nom français;PVA;Unicode Version;Date

Empty lines and # comments ignored
""",
            )

        parser.add_argument(
            '-e', '--default_english_lang',
            action='store',
            dest='default_en_lang',
            default="en",
            help='ISO 693-1 code for default language if not English (en).',
            )
        parser.add_argument(
            '-f', '--default_french_lang',
            action='store',
            dest='default_fr_lang',
            default="fr",
            help='ISO 693-1 code for default language if not French (fr).',
            )

    def handle(self, *args, **options):


        default_en_language = Language.objects.get(iso_639_1=options['default_en_lang'])
        # Check for multiple languages
        default_en_lang, default_en_lang_created = Lang.objects.get_or_create(
            language=default_en_language,
            country__isnull=True,
            script__isnull=True)
        default_en_lang.active = True
        if default_en_lang_created:
            default_en_lang.save()
            logger.info(f' -- Actived default en language: {default_en_lang}')

        default_fr_language = Language.objects.get(iso_639_1=options['default_fr_lang'])
        # Check for multiple languages
        default_fr_lang, default_fr_lang_created = Lang.objects.get_or_create(
            language=default_fr_language,
            country__isnull=True,
            script__isnull=True)
        default_fr_lang.active = True
        if default_fr_lang_created:
            default_fr_lang.save()
            logger.info(f' -- Actived default fr language: {default_fr_lang}')


        if not options['codes_file']:
            logger.error('Need a codes file!')
            return
            
        try:
            logger.info(f"Reading script codes file {options['codes_file']}")
            codes_file = open(options['codes_file'], 'r')
        except FileNotFoundError:
            logger.error(f"Script codes file {options['codes_file']} not found")
        except (OSError, IOError) as e:
            logger.error(f"Error reading script codes file {options['codes_file']}")
            raise e
        else:
            codes_file=codes_file.readlines()
            logger.info(f' -- Read len(code_data[1:]) script codes')

        total = 0
        scripts = []
        for line in codes_file[1:]:
            cleaned_line = line.strip()
            if cleaned_line == '':
                continue
            if cleaned_line[0] == "#":
                continue
            total += 1
            fields = cleaned_line.split(";")
            iso_15294 = fields[0]
            number = fields[1]
            unicode_alias = fields[4]
            unicode_version = fields[5]
            version_date = fields[6].strip()
            date_components = version_date.split('-')
            year = int(date_components[0])
            month = int(date_components[1])
            day = int(date_components[2])
            version_date = date(year, month, day)
            # Check for multiple languages
            script, script_created = Script.objects.get_or_create(iso_15294=iso_15294)
            script.code_number = number
            script.unicode_alias = unicode_alias
            script.unicode_version = unicode_version
            script.version_date = version_date
            scripts.append(script)
        # Save
        Script.objects.bulk_update(scripts, ['iso_15294','code_number','unicode_alias','unicode_version','version_date'], batch_size=50)
        logger.info(f' -- Initialized {total} Scripts')

        total = 0
        script_names = []
        for line in codes_file[1:]:
            cleaned_line = line.strip()
            if cleaned_line == '':
                continue
            if cleaned_line[0] == "#":
                continue
            fields = line.split(";")
            iso_15294 = fields[0]
            name_en = fields[2]
            name_fr = fields[3]
            # Check for multiple languages
            script = Script.objects.get(iso_15294=iso_15294)
            script_lang_en, script_lang_en_created = ScriptLang.objects.get_or_create(script=script, lang=default_en_lang)
            script_lang_en.name = name_en
            script_lang_fr, script_lang_fr_created = ScriptLang.objects.get_or_create(script=script, lang=default_fr_lang)
            script_lang_fr.name = name_fr
            script_names.append(script_lang_en)
            script_names.append(script_lang_fr)
            total += 2
        # Save
        ScriptLang.objects.bulk_update(script_names, ['script','name','lang'], batch_size=50)
        logger.info(f' -- Initialized {total} Scripts Names')

