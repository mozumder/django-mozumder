import os
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder
from mozumder.models.development import *

def CamelCase(str, separator=' '):
    return ''.join([re.sub('[^A-Za-z0-9]+', '', n).title() for n in str.split(separator)])

def camel_case_split(str, separator='_'):
    return separator.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str))


class Command(BaseCommand):

    help = 'Add a new model to an app.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            '--old',
            action='store_true',
            default=False,
            help='Use original Django app model',
            )
        parser.add_argument(
            '--verbose_name',
            action='store',
            help="Model's verbose name",
            )
        parser.add_argument(
            '--verbose_name_plural',
            action='store',
            help="Model's plural verbose name",
            )
        parser.add_argument(
            '--list_display',
            action='store',
            nargs='+',
            default = [],
            help="Fields to be shown in list display. You can also add fields by appending an asterisk - * - to the field name.",
            )
        parser.add_argument(
            '--detail_display',
            action='store',
            nargs='+',
            default = [],
            help="Fields to be shown in detail display. You can also add fields by prepending an asterisk to the field name.",
            )
        parser.add_argument(
            '--list_display_links',
            action='store',
            nargs='+',
            default = [],
            help="List display fields that link to model. You can also add fields by appending two asterisks to the field name.",
            )
        parser.add_argument(
            '--readonly_fields',
            action='store',
            nargs='+',
            default = [],
            help="Fields that are read only",
            )
        parser.add_argument(
            '--search_fields',
            action='store',
            nargs='+',
            default = [],
            help="Search fields for admin",
            )
        parser.add_argument(
            '--form_fields',
            action='store',
            nargs='+',
            default = [],
            help="Fields used in form entry",
            )
        parser.add_argument(
            'app_name',
            action='store',
            help='App name',
            )
        parser.add_argument(
            'model_name',
            action='store',
            help='Model name',
            )
        parser.add_argument(
            'field',
            action='store',
            nargs='+',
            help="""Model fields in format: name:type:[args:...] For foreignkeys, the format is: name:type:relation:on_delete:[args:...]""",
            )
            
    def handle(self, *args, **options):

        project_name = settings.PROJECT_NAME
        app_name = options['app_name']
        model_name = options['model_name']
        model_code_name = CamelCase(model_name).lower()
        verbose_name = options['verbose_name'] if options['verbose_name'] else model_name
        verbose_name_plural = options['verbose_name_plural'] if options['verbose_name_plural'] else verbose_name + 's'
        fields_list = options['field']
        list_display_links = options['list_display_links']
        list_display = options['list_display'] if options['list_display'] else options['list_display_links'].copy()
        readonly_fields = options['readonly_fields']
        search_fields = options['search_fields']
        detail_display = options['detail_display']
        form_fields = options['form_fields']
        
        # Create app
        tracked_app, app_created = TrackedApp.objects.get_or_create(name=app_name)
        tracked_app.save()

        # Create model
        tracked_model, model_crated = TrackedModel.objects.get_or_create(owner=tracked_app, name=model_name)
        tracked_model.verbose_name = verbose_name
        tracked_model.verbose_name_plural = verbose_name_plural
        tracked_model.save()

        # Build models lists
        show_in_detail_view = False
        show_in_edit_view = False
        show_in_list_view = False
        link_in_list_view = False
        blank = False
        null = False
        for field in fields_list:
            field_name, field_type, field_properties, *field_params = field.split(":")
            if 'r' in field_properties:
                show_in_detail_view = True
            if 'e' in field_properties:
                show_in_edit_view = True
            if 'l' in field_properties:
                show_in_list_view = True
            if 'L' in field_properties:
                show_in_list_view = True
                link_in_list_view = True
            if '_' in field_properties:
                blank = True
            if '-' in field_properties:
                null = True
            
            field = TrackedField.objects.get_or_create(name=field_name, owner=tracked_model)
            field.show_in_detail_view = show_in_detail_view
            field.show_in_edit_view = show_in_edit_view
            field.show_in_list_view = show_in_list_view
            field.link_in_list_view = link_in_list_view
            field.blank = blank
            field.null = null

            if field_type == 'CharField':
            elif field_type == 'TextField':
            elif field_type == 'SmallIntegerField':
            elif field_type == 'DateTimeField':
            elif field_type == 'ForeignKey':
                relation = field_params[0]
                on_delete = field_params[1]
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        related_name = param.split('=')[1]
                    i += 1
            elif field_type == 'ManyToManyField':
                relation = field_params[0]
                field_params[0] = f"'{relation}'"
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        related_name = param.split('=')[1]
                    i += 1
                    
            field.save()

        # Build models lists
        model = f'class {model_name}(models.Model):\n'
        admin = ''
        fields = []
        for field in fields_list:
            field_name, field_type, *field_params = field.split(":")
            fields.append(field_name.strip('*').strip('_'))
            if field_name.startswith('*'):
                field_name = field_name[1:]
                detail_display.append(field_name.strip('*').strip('_'))
            if field_name.startswith('_'):
                field_name = field_name[1:]
                form_fields.append(field_name.strip('*').strip('_'))
            if field_name.endswith('**'):
                field_name = field_name[:-2]
                list_display.append(field_name.strip('*'))
                list_display_links.append(field_name.strip('*').strip('_'))
            elif field_name.endswith('*'):
                field_name = field_name[:-1]
                list_display.append(field_name.strip('*').strip('_'))
            if field_type == 'ForeignKey':
                relation = field_params[0]
                field_params[0] = f"'{relation}'"
                on_delete = field_params[1]
                field_params[1] = f'on_delete=models.{on_delete}'
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        related_name = param.split('=')[1]
                        field_params[i] = f"related_name='{related_name}'"
                    i += 1
            elif field_type == 'ManyToManyField':
                relation = field_params[0]
                field_params[0] = f"'{relation}'"
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        related_name = param.split('=')[1]
                        field_params[i] = f"related_name='{related_name}'"
                    i += 1
            field_args = ", ".join(field_params)
            field_line = f'    {field_name}=models.{field_type}({field_args})\n'
            model += field_line
        model += f"""    def get_absolute_url(self):
        return reverse('{model_code_name}_detail', kwargs={{'pk': self.id}})\n"""

        update_models_file()
        write_admin_file()
        update_urls_file()
        write_views_file()
        write_list_block()
        write_list_page()
        write_detail_block()
        write_detail_page()
        update_app_model_list_block()
        write_create_form_block()
        write_create_form_page()
        write_update_form_block()
        write_update_form_page()
        write_delete_form_block()
        write_delete_form_page()
        write_copy_form_block()
        write_copy_form_page()


