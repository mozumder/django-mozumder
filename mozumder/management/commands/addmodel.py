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
        model = f'class {model_name}(models.Model):\n'
        admin = ''
        list_display_links = options['list_display_links']
        list_display = options['list_display'] if options['list_display'] else options['list_display_links'].copy()
        readonly_fields = options['readonly_fields']
        search_fields = options['search_fields']
        detail_display = options['detail_display']
        for field in fields_list:
            field_name, field_type, *field_params = field.split(":")
            if field_name.startswith('*'):
                field_name = field_name[1:]
                detail_display.append(field_name.strip('*'))
            if field_name.endswith('**'):
                field_name = field_name[:-2]
                list_display.append(field_name.strip('*'))
                list_display_links.append(field_name.strip('*'))
            elif field_name.endswith('*'):
                field_name = field_name[:-1]
                list_display.append(field_name.strip('*'))
                print(f'3 {list_display=}')
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
                    line += f"""from ..views import *

"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{model_code_name}/', {model_name}ListView.as_view(), name='{model_code_name}_list'),\n"
                    output += f"    path('{model_code_name}/add', {model_name}AddView.as_view(), name='{model_code_name}_add'),\n"
                    output += f"    path('{model_code_name}/<int:pk>', {model_name}DetailView.as_view(), name='{model_code_name}_detail'),\n"
                    output += f"    path('{model_code_name}/<int:pk>/update', {model_name}UpdateView.as_view(), name='{model_code_name}_update'),\n"
                    output += f"    path('{model_code_name}/<int:pk>/copy', {model_name}CopyView.as_view(), name='{model_code_name}_copy'),\n"
                    output += f"    path('{model_code_name}/<int:pk>/delete', {model_name}DeleteView.as_view(), name='{model_code_name}_delete'),\n"
                    output += f"    path('search/{model_code_name}', search_{model_code_name}, name='search_{model_code_name}'),\n"
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
                    line += f"""from ...views import *
                    
"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{model_code_name}/', {model_name}JSONListView.as_view(), name='json_{model_code_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field
                    output += f"    path('{model_code_name}/<int:pk>', {model_name}JSONDetailView.as_view(), name='json_{model_code_name}_detail'),\n"
                    output += f"    path('search/{model_code_name}', json_search_{model_code_name}, name='search_{model_code_name}'),\n"
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

class {model_name}ListView(ListView):
    model = {model_name}

class {model_name}AddView(ListView):
    model = {model_name}

class {model_name}CopyView(DetailView):
    model = {model_name}

class {model_name}UpdateView(DetailView):
    model = {model_name}

class {model_name}DeleteView(DetailView):
    model = {model_name}

def search_{model_code_name}():
    pass

class {model_name}JSONDetailView(DetailView):
    model = {model_name}

class {model_name}JSONListView(ListView):
    model = {model_name}

def json_search_{model_code_name}():
    pass
"""
        f.close()
        f = open(views_file, "w")
        f.write(output)
        f.close()

        # Model List Block
        header_row = ''
        row = ''
        for field in list_display:
            header_row += f'<th>{field}</th>'
            if field in list_display_links:
                row += f"""<td><a href="{{% url '{model_code_name}_update' instance.id %}}">{{{{instance.{field}}}}}</a></td>"""
            else:
                row += f'<td>{{{{instance.{field}}}}}</td>'
        models_list_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_list_block.html')
        f = open(models_list_block_file, "w")
        f.write(f"""<table>
<tr>{header_row}</tr>
{{% for instance in object_list %}}
<tr>{ row }</tr>
{{% endfor %}}
</table>""")
        f.close()

        # Model List Page
        models_list_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_list.html')
        f = open(models_list_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name_plural}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name_plural }</H1>
{{% include "{app_name}/{model_code_name}_list_block.html" %}}
{{% endblock content %}}
""")
        f.close()

        field_ul = ''
        for field in detail_display:
            field_ul += f"<li>{{{{{model_code_name}.{field}}}}}</li>"

        # Model Detail Block
        models_detail_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_detail_block.html')
        f = open(models_detail_block_file, "w")
        f.write(f'<div>Model Detail</div>\n<ul>{field_ul}</ul>')
        f.close()

        # Model Detail Page
        models_detail_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_detail.html')
        f = open(models_detail_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name }</H1>
{{% include "{app_name}/{model_code_name}_detail_block.html" %}}
{{% endblock content %}}
""")
        f.close()


        # Add model to app's models list HTML
        models_ul = f"""<li><a href="{{% url '{model_code_name}_list' %}}">{verbose_name}</a> <a href="{{% url '{model_code_name}_add' %}}">Add</a></li>"""
        models_list_html_file = os.path.join(os.getcwd(),app_name,'templates',app_name, 'models.html')
        f = open(models_list_html_file, "a")
        f.write(models_ul)
        f.close()

        # Write forms.py file
