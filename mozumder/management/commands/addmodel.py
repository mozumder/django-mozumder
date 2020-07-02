import os
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder

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
        verbose_name = options['verbose_name']
        verbose_name_plural = options['verbose_name_plural']
        model_name = options['model_name']
        model_code_name = CamelCase(model_name).lower()
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
                    line += f"""from ..views import ({model_name}ListView, {model_name}DetailView,
    search_{model_code_name}, {model_name}StubsView, {model_name}StubView)

"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{model_code_name}/', {model_name}ListView.as_view(), name='{model_code_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field
                    output += f"    path('{model_code_name}/<int:pk>', {model_name}DetailView.as_view(), name='{model_code_name}_detail'),\n"
                    output += f"    path('search/{model_code_name}', search_{model_code_name}, name='search_{model_code_name}'),\n"
                    output += f"    path('stub/{model_code_name}', {model_name}StubsView.as_view(), name='{model_code_name}_stub'),\n"
                    output += f"    path('stub/{model_code_name}/<int:pk>', {model_name}StubView.as_view(), name='{model_code_name}_stubs'),\n"
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
                    line += f"""from ...views import ({model_name}JSONListView, {model_name}JSONDetailView,
    json_search_{model_code_name}, {model_name}JSONStubsView, {model_name}JSONStubView)

"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{model_code_name}/', {model_name}JSONListView.as_view(), name='json_{model_code_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field
                    output += f"    path('{model_code_name}/<int:pk>', {model_name}JSONDetailView.as_view(), name='json_{model_code_name}_detail'),\n"
                    output += f"    path('search/{model_code_name}', json_search_{model_code_name}, name='search_{model_code_name}'),\n"
                    output += f"    path('stub/{model_code_name}', {model_name}JSONStubsView.as_view(), name='json_{model_code_name}_stub'),\n"
                    output += f"    path('stub/{model_code_name}/<int:pk>', {model_name}JSONStubView.as_view(), name='json_{model_code_name}_stubs'),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()

        # Write views.py file
        views_file = os.path.join(os.getcwd(),app_name,'views.py')

        f = open(views_file, "r")
        output = ''
        state = 'file'
        imported = False
        for line in f.readlines():
            if line.startswith("from django.views.generic import ListView, DetailView, View"):
                imported = True
            elif line.startswith('# Create your views here.'):
                output += f"from .models import {model_name}\n"
                if imported == False:
                    output += f"from django.views.generic import ListView, DetailView, View\n"
                    imported = True
            output += line

        output += f"""
class {model_name}DetailView(DetailView):
    model = {model_name}
    template = 'detail.html'

class {model_name}ListView(ListView):
    model = {model_name}
    template = 'list.html'

class {model_name}StubView(DetailView):
    model = {model_name}
    template = 'stub.html'

class {model_name}StubsView(ListView):
    model = {model_name}
    template = 'stubs.html'

def search_{model_code_name}():
    pass

class {model_name}JSONDetailView(DetailView):
    model = {model_name}
    template = 'json_detail.html'

class {model_name}JSONListView(ListView):
    model = {model_name}
    template = 'json_list.html'

class {model_name}JSONStubView(DetailView):
    model = {model_name}
    template = 'json_stub.html'

class {model_name}JSONStubsView(ListView):
    model = {model_name}
    template = 'json_stubs.html'

def json_search_{model_code_name}():
    pass
"""
        f.close()
        f = open(views_file, "w")
        f.write(output)
        f.close()

        # Write Templates
        
        #Add model to Homepage
        models_html_file = os.path.join(os.getcwd(),project_name,'template','models.html')

        f = open(models_html_file, "r")
        output = ''
        for line in f.readlines():
            if line.startswith("</table>"):
                imported = True
                output += f"""<tr><td>{model_name}</td><td><a href="{{% url '{model_code_name}_list' %}}">List</a></td></tr>\n"""
            output += line
        f.close()
        
        f = open(models_html_file, "w")
        f.write(output)
        f.close()

        # Write views.py file

        # Write forms.py file

