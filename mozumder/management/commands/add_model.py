import os

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder
from ...models.development import *
from ... import FieldTypes, OnDelete
from ..utilities.modelwriter import *
from ..utilities.name_case import *

class Command(BaseCommand):

    help = 'Add a new model to an app.'
    
    def add_arguments(self, parser):

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
            help="Model fields in format: name:type:[args:...] For foreignkeys, the format is: name:type:relation:on_delete:[args:...]",
            )
            
    def handle(self, *args, **options):

        project_name = settings.PROJECT_NAME
        app_name = options['app_name']
        model_name = options['model_name']
        model_code_name = CamelCase_to_snake_case(model_name)
        verbose_name = options['verbose_name'] if options['verbose_name'] else CamelCase_to_verbose(model_name)
        verbose_name_plural = options['verbose_name_plural'] if options['verbose_name_plural'] else verbose_name + 's'
        fields_list = options['field']
        
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
        editable = True
        show_in_list_view = False
        link_in_list_view = False
        db_tablespace = None
        db_column = None
        db_index = False
        blank = False
        null = False
        error_messages = {}
        validators = []
        help_text = None
        primary_key = False
        unique = False
        unique_for_date = False
        unique_for_month = False
        unique_for_year = False
        auto_now = False
        auto_now_add = False

        auto_created = False
        serialize = True

        has_primary_key = False

        for field in fields_list:
            field_name, field_type, field_properties, *field_params = field.split(":")

            field, field_created = TrackedField.objects.get_or_create(name=field_name, owner=tracked_model)
            
            field.verbose_name = snake_case_to_verbose(field_name)

            # Get field properties
            if 'p' in field_properties:
                field.primary_key = True
                has_primary_key = True
            if '_' in field_properties:
                field.null = True
            if '-' in field_properties:
                field.blank = True
                field.null = True
            if 'r' in field_properties:
                field.show_in_detail_view = True
            if 'e' in field_properties:
                field.show_in_edit_view = True
            if 'l' in field_properties:
                field.show_in_list_view = True
            if 'L' in field_properties:
                field.show_in_list_view = True
                field.link_in_list_view = True
            if 'i' in field_properties:
                field.db_index = True
            if 'k' in field_properties:
                field.primary_key = True
            if 'U' in field_properties:
                field.unique = True
            if 'D' in field_properties:
                field.unique_for_date = True
            if 'M' in field_properties:
                field.unique_for_month = True
            if 'Y' in field_properties:
                field.unique_for_year = True
            if 'a' in field_properties:
                field.auto_now = True
            if 'A' in field_properties:
                field.auto_now_add = True
            
            if field_type == 'BooleanField':
                if len(field_params) > 0:
                    field.default_bool = field_params[0]
            elif field_type == 'CharField':
                field.max_length = int(field_params[0]) if field_params[0] else None
                if len(field_params) > 1:
                    field.default_text = field_params[1] if field_params[1] else None
            elif field_type == 'BinaryField':
                field.max_length = int(field_params[0]) if field_params[0] else None
            elif field_type == 'TextField':
                if len(field_params) > 0:
                    field.default_text = field_params[0] if field_params[1] else None
            elif field_type == 'SmallIntegerField':
                if len(field_params) > 0:
                    field.default_smallint = int(field_params[0]) if field_params[0] else None
            elif field_type == 'BigIntegerField':
                if len(field_params) > 0:
                    field.default_bigint = int(field_params[0]) if field_params[0] else None
            elif field_type == 'DateTimeField':
                if len(field_params) > 0:
                    field.default_datetime = field_params[0]
            elif field_type == 'ForeignKey':
                field.to = field_params[0]
                field.on_delete = OnDelete[field_params[1]]
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        field.related_name = param.split('=')[1]
                    i += 1
            elif field_type == 'ManyToManyField':
                field.to = field_params[0]
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        field.related_name = param.split('=')[1]
                    i += 1
            elif field_type == 'ImageField' or field_type == 'FileField':
                i = 0
                for param in field_params:
                    if param.startswith('upload_to='):
                        field.upload_to = param.split('=')[1]
                    i += 1
            field.type=FieldTypes[field_type.upper()]
            field.save()

        if has_primary_key == False:
            field, field_created = TrackedField.objects.get_or_create(
                name='id', owner=tracked_model)
            field.type=FieldTypes['AUTOFIELD']
            field.auto_created = True
            field.primary_key = True
            field.serialize = False
            field.verbose_name = 'ID'
            field.save()

