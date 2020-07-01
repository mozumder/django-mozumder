import os

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder

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
            help='Model verbose name',
            )
        parser.add_argument(
            '--verbose_name_plural',
            action='store',
            help='Model plural verbose name',
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

        app_name = options['app_name']
        model_name = options['model_name']
        fields_list = options['field']
        model = f'class {model_name}(models.Model):\n'
        admin = ''
        list_display = ['id']
        list_display_links = ['id']
        readonly_fields= []
        search_fields = []

        for field in fields_list:
            field_name, field_type, *field_params = field.split(":")
            if field_name.endswith('**'):
                field_name = field_name[:-2]
                list_display.append(field_name)
                list_display_links.append(field_name)
            elif field_name.endswith('*'):
                field_name = field_name[:-1]
                list_display.append(field_name)
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
        model += '\n'

        # Write models.py file
        models_file = os.path.join(os.getcwd(),app_name,'models.py')
        f = open(models_file, "a")
        f.write(model)
        f.close()

        # Create admin data
        if list_display or list_display_links or readonly_fields or search_fields:
            admin = f'\n@admin.register({model_name})\nclass {model_name}Admin(admin.ModelAdmin):\n'
            if list_display:
                admin += f"    list_display={', '.join(map(str, [list_display]))}\n"
            if list_display_links:
                admin += f"    list_display_links={', '.join(map(str, [list_display_links]))}\n"
            if readonly_fields:
                admin += f"    readonly_fields={', '.join(map(str, [readonly_fields]))}\n"
            if search_fields:
                admin += f"    search_fields={', '.join(map(str, [search_fields]))}\n"
            admin += '\n'

        # Write admin.py file
        admin_file = os.path.join(os.getcwd(),app_name,'admin.py')
        f = open(admin_file, "r")
        file = ''
        for line in f.readlines():
            if line.startswith("# Register your models here."):
                file += f'from .models import {model_name}\n'
            file += line
        file += admin
        
        f = open(admin_file, "w")
        f.write(file)
        f.close()

        # The following are the operations that are built by default for
        # every model:
        #
        # Read One Item
        # Read All
        # Read Filter/Exclude
        # Search Items
        # Sort Items
        # Reorder Items
        # Add One Item
        # Add Multiple Items
        # Duplicate Item
        # Update Item
        # Update All
        # Update Filter/Exclude
        # Validate Item
        # Delete Item
        # Delete All
        # Delete Filter/Exclude
        # Search Through Field
        # Add Item to Field
        # Add Multiple Items to Field
        # Increment Field
        # Decrement Field
        # Validate Field
        # Duplicate Items to Field
        # Delete Item from Field
        # Delete All Items from Field
        # Delete Multiple Items from Field
        # Operation on View
        #
        # Disable operations you don't need by commenting out the operation in
        # the urls.py file
        
        # Write urls.py file

        # Write views.py file

        # Write forms.py file

        # Write Templates
