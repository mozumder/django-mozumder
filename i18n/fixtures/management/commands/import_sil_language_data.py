from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from datetime import date
import logging

from i18n.models import Language, LanguageLang, MacroLanguageMapping, RetiredLanguage, Lang

logger = logging.getLogger("management")

class Command(BaseCommand):
    """ Download ISO code tables from:
    https://iso639-3.sil.org/code_tables/download_tables"""

    help = 'Imports SIL.ORG ISO 693 language code tables'

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--codes_file',
            action='store',
            dest='codes_file',
            default='i18n/fixtures/iso-639-3_Code_Tables_20200130/iso-639-3_20200130.tab',
            help='Tab delimited file of Id, Part2B, Part2T, Part1, Scope, Language_Type, Ref_Name, & Comment. First line ignored',
            )
        parser.add_argument(
            '-n', '--names_file',
            action='store',
            dest='names_file',
            default='i18n/fixtures/iso-639-3_Code_Tables_20200130/iso-639-3_Name_Index_20200130.tab',
            help='Tab delimited file of Id, Print_Name, & Inverted_Name. First line ignored',
            )
        parser.add_argument(
            '-r', '--retirements_file',
            action='store',
            dest='retirements_file',
            default='i18n/fixtures/iso-639-3_Code_Tables_20200130/iso-639-3_Retirements_20200130.tab',
            help='Tab delimited file of Id, Ref_Name, Ret_Reason, Change_To, Ret_Remedy, & Effective. First line ignored',
            )
        parser.add_argument(
            '-m', '--macrolanguages_file',
            action='store',
            dest='macrolanguages_file',
            default='i18n/fixtures/iso-639-3_Code_Tables_20200130/iso-639-3-macrolanguages_20200130.tab',
            help='Tab delimited file of M_Id, I_Id, I_Status. First line ignored',
            )
        parser.add_argument(
            '-d', '--datestamp',
            action='store',
            dest='date',
            default=False,
            help='Data datestamp, in YYYYMMDD format',
            )
        parser.add_argument(
            '-l', '--default_lang',
            action='store',
            dest='default_lang',
            default="eng",
            help='ISO 693-3 code for default language if not English (eng).',
            )
        parser.add_argument(
            '--init_only',
            action='store_true',
            dest='init_only',
            default=False,
            help='Data datestamp, in YYYYMMDD format',
            )

    def handle(self, *args, **options):

        if not options['codes_file']:
            logger.error('Need a codes file!')
            return
            
        try:
            codes_file = open(options['codes_file'], 'r')
            logger.info('Reading language codes file %s' % options['codes_file'])
        except FileNotFoundError:
            logger.error('language codes file %s not found' % options['codes_file'])
        except (OSError, IOError) as e:
            logger.error('Error reading language codes file %s' % options['codes_file'])
            raise e
        else:
            code_data=codes_file.readlines()
            logger.info(' -- Read %i language codes' % len(code_data[1:]))

        total = 0
        languages = []
        for line in code_data[1:]:
            line = line.rstrip("\n")
            fields = line.split("\t")
            if len(fields)>7:
                total += 1
                iso_639_3 = fields[0]
                iso_639_2b = fields[1]
                iso_639_2t = fields[2]
                iso_639_1 = fields[3]
                scope = fields[4]
                language_type = fields[5]
                ref_name = fields[6]
                comment = fields[7]
                # Check for multiple languages
                language, language_created = Language.objects.get_or_create(iso_639_3=iso_639_3)

                if iso_639_2b:
                    language.iso_639_2b = iso_639_2b
                else:
                    language.iso_639_2b = None

                if iso_639_2t:
                    language.iso_639_2t = iso_639_2t
                else:
                    language.iso_639_2t = None

                if iso_639_1:
                    language.iso_639_1 = iso_639_1
                else:
                    language.iso_639_1 = None

                if scope:
                    language.scope = scope
                else:
                    language.scope = None

                if language_type:
                    language.type = language_type
                else:
                    language.type = None
                languages.append(language)
        # Save
        Language.objects.bulk_update(languages, ['iso_639_3','iso_639_2b','iso_639_2t','iso_639_1','scope','type'], batch_size=50)
        logger.info(' -- Initialized %s Languages' % total)

        default_language = Language.objects.get(iso_639_3=options['default_lang'])
        # Check for multiple languages
        default_lang, default_lang_created = Lang.objects.get_or_create(
            language=default_language,
            country__isnull=True,
            script__isnull=True)
        default_lang.active = True
        if default_lang_created:
            default_lang.save()
            logger.info(' -- Actived default language: %s' % default_lang)

        language_langs = []
        total = 0
        for line in code_data[1:]:
            line = line.rstrip("\n")
            fields = line.split("\t")
            if len(fields)>7:
                total += 1
                iso_639_3 = fields[0]
                ref_name = fields[6]
                comment = fields[7]
                if comment == '':
                    comment = None
                language = Language.objects.get(iso_639_3=iso_639_3)
                language_lang, language_lang_created = LanguageLang.objects.get_or_create(
                    language=language,
                    print_name=ref_name,
                    lang=default_lang)
                language_lang.inverted_name = ref_name
                language_lang.ref_name = True
                language_lang.comment = comment
                language_langs.append(language_lang)
        # Save
        LanguageLang.objects.bulk_update(language_langs, ['language','lang','print_name','inverted_name','ref_name','comment'], batch_size=50)
        logger.info(' -- Initialized %i Languages names' % total)

        if not options['names_file']:
            logger.info('Need a names file!')
            return
            
        try:
            names_file = open(options['names_file'], 'r')
            logger.info('Reading names file %s' % options['names_file'])
        except FileNotFoundError:
            logger.error('Names file %s not found' % options['names_file'])
        except (OSError, IOError) as e:
            logger.error('Error reading names file %s' % options['names_file'])
            raise e
        else:
            names_data=names_file.readlines()
            logger.info(' -- Read %i language names' % len(names_data[1:]))

        language_langs = []
        total = 0
        extras = 0
        for line in names_data[1:]:
            line = line.rstrip("\n")
            fields = line.split("\t")
#            print(fields)
            total += 1
            iso_639_3 = fields[0]
            print_name = fields[1]
            inverted_name = fields[2]
            try:
                language = Language.objects.get(iso_639_3=iso_639_3)
            except ObjectDoesNotExist:
                logger.warning(f'Language "{iso_639_3}" does not exist')
                logger.warning(f"File {options['names_file']} in line number {total}")
                continue
            language_lang, language_lang_created = LanguageLang.objects.get_or_create(
                language=language,
                lang=default_lang,
                print_name=print_name,
            )
            language_lang.inverted_name = inverted_name
            language_lang.comment = comment
            if language_lang.ref_name == False:
                extras += 1
            language_langs.append(language_lang)
        # Save
        LanguageLang.objects.bulk_update(language_langs, ['language','lang','print_name','inverted_name','ref_name','comment'], batch_size=50)
        logger.info(' -- Updated %i language names with %i extra names' % (total, extras))


        if not options['retirements_file']:
            logger.error('Need a retirements file!')
            return
        try:
            retirements_file = open(options['retirements_file'], 'r')
            logger.info('Reading retirements file %s' % options['retirements_file'])
        except FileNotFoundError:
            logger.error('Retirements file %s not found' % options['retirements_file'])
        except (OSError, IOError) as e:
            logger.error('Error reading retirements file %s' % options['retirements_file'])
            raise e
        else:
            retirements_data=retirements_file.readlines()
            logger.info(' -- Read %i language retirements' % len(retirements_data[1:]))

        retired_languages = []
        total = 0
        for line in retirements_data[1:]:
            line = line.rstrip("\n")
            fields = line.split("\t")
            total += 1
            iso_639_3 = fields[0]
            ref_name = fields[1]
            ret_reason = fields[2]
            change_to = fields[3]
            if change_to == '':
                change_to = None
            ret_remedy = fields[4]
            if ret_remedy == '':
                ret_remedy = None
            effective_date = fields[5]
            if effective_date == '':
                effective_date = None
            else:
                components = effective_date.split('-')
                effective_date = date(int(components[0]), int(components[1]), int(components[2]))
            retired_language, retired_language_created = RetiredLanguage.objects.get_or_create(iso_639_3=iso_639_3)
            retired_language.ref_name = ref_name
            retired_language.reason = ret_reason
            retired_language.change_to = change_to
            retired_language.ret_remedy = ret_remedy
            retired_language.effective_date = effective_date
            
            retired_languages.append(retired_language)
        # Save
        RetiredLanguage.objects.bulk_update(retired_languages, ['iso_639_3','ref_name','reason','change_to','ret_remedy','effective_date'], batch_size=50)
        logger.info(' -- Updated %i Language retirements' % total)


        if not options['macrolanguages_file']:
            logger.error('Need a Macrolanguages file!')
            return
        try:
            macrolanguages_file = open(options['macrolanguages_file'], 'r')
            logger.info('Reading retirements file %s' % options['macrolanguages_file'])
        except FileNotFoundError:
            logger.error('Retirements file %s not found' % options['macrolanguages_file'])
        except (OSError, IOError) as e:
            logger.error('Error reading retirements file %s' % options['macrolanguages_file'])
            raise e
        else:
            macrolanguages_data=macrolanguages_file.readlines()
            logger.info(' -- Read %i macrolanguage mappings' % len(macrolanguages_data[1:]))

        macrolanguage_mappings = []
        total = 0
        for line in macrolanguages_data[1:]:
            line = line.rstrip('\n')
            fields = line.split("\t")
            total += 1
            macrolanguage_iso = fields[0]
            individual_language_iso = fields[1]
            status = fields[2].strip()
            macrolanguage = Language.objects.get(iso_639_3=macrolanguage_iso)
            if status == 'R':
                individual_language = None
                retired_individual_language = RetiredLanguage.objects.get(iso_639_3=individual_language_iso)
            else:
                individual_language = Language.objects.get(iso_639_3=individual_language_iso)
                retired_individual_language = None
            macrolanguage_mapping, macrolanguage_mapping_created = MacroLanguageMapping.objects.get_or_create(
                macrolanguage=macrolanguage,
                individual_language=individual_language,
                retired_individual_language=retired_individual_language)
            macrolanguage_mapping.status = status
            macrolanguage_mappings.append(macrolanguage_mapping)
        # Save
        MacroLanguageMapping.objects.bulk_update(macrolanguage_mappings, ['macrolanguage','individual_language','retired_individual_language','status'], batch_size=50)
        logger.info(' -- Updated %i Macrolanguage mappings' % total)
