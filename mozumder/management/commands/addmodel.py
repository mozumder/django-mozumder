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
        # Read Stubs List
        # Search Items
        # Sort Items
        # Reorder Items
        # Add One Item
        # Insert One Item
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
        # Enable operations you need by uncommenting out the operation in
        # the urls.py file
        
        # Write urls.py file
        # Edit base URLs py
        urls_file = os.path.join(os.getcwd(),app_name,'urls','__init__.py')

        f = open(urls_file, "r")
        output = ''
        state = 'file'
        for line in f.readlines():
            if state == 'file':
                if line.startswith('urlpatterns = [\n'):
                    state = 'urlpatterns'
                elif line.startswith("from django.urls import path"):
                    line += f"""from ..views import ({model_name}View, {model_name}DetailView,
    search_{model_name}, copy_{model_name})
"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field, HEAD: Read Stubs List
                    output += f"    #path('{model_name}/', {model_name}ListView.as_view(), name='{model_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field, HEAD: Read Stub
                    output += f"    #path('{model_name}/<int:pk>', {model_name}DetailView.as_view(), name='{model_name}_detail'),\n"
                    output += f"    #path('search/{model_name}', {model_name}SearchView.as_view(), name='search_{model_name}'),\n"
                    output += f"    #path('copy/{model_name}/<int:pk>', copy_{model_name}, name='copy_{model_name}'),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()

        # Edit base URLs py
        urls_file = os.path.join(os.getcwd(),app_name,'urls','api','__init__.py')

        f = open(urls_file, "r")
        output = ''
        state = 'file'
        for line in f.readlines():
            if state == 'file':
                if line.startswith('urlpatterns = [\n'):
                    state = 'urlpatterns'
                elif line.startswith("from django.urls import path"):
                    line += f"""from ..views import ({model_name}JSONView, {model_name}JSONDetailView,
    json_search_{model_name}, json_copy_{model_name})
"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field, HEAD: Read Stubs List
                    output += f"    #path('{model_name}/', {model_name}JSONListView.as_view(), name='json_{model_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field, HEAD: Read Stub
                    output += f"    #path('{model_name}/<int:pk>', {model_name}JSONDetailView.as_view(), name='json_{model_name}_detail'),\n"
                    output += f"    #path('search/{model_name}', {model_name}JSONSearchView.as_view(), name='json_search_{model_name}'),\n"
                    output += f"    #path('copy/{model_name}/<int:pk>', json_copy_{model_name}, name='json_copy_{model_name}'),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()

        # Write views.py file

        # Write forms.py file

        # Write Templates
