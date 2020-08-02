import os

from ...models import *
from ..utilities.name_case import *

from dotmap import DotMap

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

class DevelopTemplate:

    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir

    def get_filename(self, context):
        # Subclass this as needed
        return f"{context['model_code_name']}{self.extension}"
    def get_filepath(self, context):
        # Subclass this as needed
        return os.path.join(os.getcwd(),context['app_name'],self.template_dir,context['app_name'])

    def write(self, context):
        file = os.path.join(self.get_filepath(context),self.get_filename(context))
        print(f'Writing file: {file}')
        f = open(file, "w")
        f.write(self.get_text(DotMap(context)))
        f.close()


class ModelsFile(DevelopTemplate):
    extension = ".py"
    def get_filename(self, context):
        return 'models.py'
    def get_filepath(self, context):
        # Subclass this as needed
        return os.path.join(os.getcwd(),context['app_name'])

    def get_model_text(self, model_obj, context):
        output = f"class {model_obj.name}(models.Model):\n"
        fields = TrackedField.objects.filter(owner=model_obj)
        for field in fields:
            field_params = {}
            field_param_pairs = []
            if FieldTypes(field.type).label == 'ForeignKey':
                field_param_pairs += ["'" + field.to + "'"]
                field_params['on_delete'] = 'models.' + str(OnDelete(field.on_delete).label)
            if FieldTypes(field.type).label == 'ManyToManyField':
                field_param_pairs += ["'" + field.to + "'"]
            if snake_case_to_verbose(field.name) != field.verbose_name:
                field_param_pairs += ["_(" + field.verbose_name + ")"]
            if field.related_name:
                field_params['related_name'] = "'" + field.related_name + "'"
            if field.max_length:
                field_params['max_length'] = field.max_length
            if field.default_bool == True:
                field_params['default'] = True
            if field.default_bool == False:
                field_params['default'] = False
            if field.default_text:
                field_params['default'] = "'" + field.default_text + "'"
            if field.default_smallint:
                field_params['default'] = field.default_smallint
            if field.auto_now == True:
                field_params['auto_now'] = True
            if field.auto_now_add == True:
                field_params['auto_now_add'] = True
            if field.null == True:
                field_params['null'] = True
            if field.blank == True:
                field_params['blank'] = True
            if field.db_index == True:
                field_params['db_index'] = True
            if field.primary_key == True:
                field_params['primary_key'] = True
            if field.unique == True:
                field_params['unique'] = True
            if field.unique_for_date == True:
                field_params['unique_for_date'] = True
            if field.unique_for_month == True:
                field_params['unique_for_month'] = True
            if field.unique_for_year == True:
                field_params['unique_for_year'] = True
            field_param_pairs += [f'{k}={v}' for k, v in field_params.items()]
            
            line = f"    {field.name} = models.{FieldTypes(field.type).label}({', '.join(field_param_pairs)})\n"
            output += line
        output += "\n"
        return output

    def get_text(self, context):

        output = f"""from django.db import models
from django.utils.translation import gettext as _

# Create your models here
"""
        app_obj = TrackedApp.objects.get(name=context.app_name)
        model_objs = TrackedModel.objects.filter(owner=app_obj)
        for model_obj in model_objs:
            output += self.get_model_text(model_obj, context)
        return output

class AdminPy(DevelopTemplate):

    def get_text(self, context):

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
                file += f"""from django.urls import reverse
from .models import {model_name}
"""
            file += line
        file += admin
        
        f = open(admin_file, "w")
        f.write(file)
        f.close()

        
class URLSPy(DevelopTemplate):

    def get_text(self, context):
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

class BaseURLSPy(DevelopTemplate):

    def get_text(self, context):
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

class ViewsPy(DevelopTemplate):

    def get_text(self, context):
        # Write views.py file
        views_file = os.path.join(os.getcwd(),app_name,'views.py')

        f = open(views_file, "r")
        output = ''
        state = 'file'
        imported = False
        for line in f.readlines():
            if line.startswith("from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, DeleteView"):
                imported = True
            elif line.startswith('# Create your views here.'):
                output += f"from .models import {model_name}\n"
                if imported == False:
                    output += f"""from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, \
    UpdateView, DeleteView
"""
                    imported = True
            output += line

        output += f"""
class {model_name}DetailView(DetailView):
    model = {model_name}

class {model_name}ListView(ListView):
    model = {model_name}

class {model_name}AddView(CreateView):
    model = {model_name}
    fields = {form_fields}
    template_name_suffix = '_create_form'

class {model_name}CopyView(UpdateView):
    model = {model_name}
    fields = {form_fields}
    template_name_suffix = '_copy_form'

class {model_name}UpdateView(UpdateView):
    model = {model_name}
    fields = {form_fields}
    template_name_suffix = '_update_form'

class {model_name}DeleteView(DeleteView):
    model = {model_name}
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('{model_code_name}_list')

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

class ModelListBlock(DevelopTemplate):

    def get_text(self, context):
        # Model List Block
        header_row = ''
        row = ''
        for field in list_display:
            header_row += f'<th>{field}</th>'
            if field in list_display_links:
                row += f"""<td>{{{{instance.{field}}}}}</td>"""
            else:
                row += f"""<td><a href="{{% url '{model_code_name}_detail' instance.id %}}">{{{{instance.{field}}}}}</a></td>"""
        header_row += '<th></th><th></th><th></th>'
        row += f"""<td><a href="{{% url '{model_code_name}_copy' instance.id %}}">Copy</a></td><td><a href="{{% url '{model_code_name}_update' instance.id %}}">Edit</a></td><td><a href="{{% url '{model_code_name}_delete' instance.id %}}">Delete</a></td>"""
        models_list_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_list_block.html')
        f = open(models_list_block_file, "w")
        f.write(f"""<table>
<tr>{header_row}</tr>
{{% for instance in object_list %}}
<tr>{ row }</tr>
{{% endfor %}}
</table>""")
        f.close()

class ModelListPage(DevelopTemplate):

    def get_text(self, context):
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

class ModelDetailPage(DevelopTemplate):

    def get_text(self, context):
        # Model Detail Block
        field_ul = ''
        for field in detail_display:
            field_ul += f"<li>{{{{{model_code_name}.{field}}}}}</li>"

        models_detail_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_detail_block.html')
        f = open(models_detail_block_file, "w")
        f.write(f'<div>Model Detail</div>\n<ul>{field_ul}</ul>')
        f.close()

class ModelDetailPage(DevelopTemplate):

    def get_text(self, context):
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

class UpdateModelsListBlock(DevelopTemplate):

    def get_text(self, context):
        # Add model to app's models list HTML
        models_ul = f"""<li><a href="{{% url '{model_code_name}_list' %}}">{verbose_name}</a> <a href="{{% url '{model_code_name}_add' %}}">Add</a></li>"""
        models_list_html_file = os.path.join(os.getcwd(),app_name,'templates',app_name, 'models.html')
        f = open(models_list_html_file, "a")
        f.write(models_ul)
        f.close()

class CreateFormBlock(DevelopTemplate):
    extension = '_create_form_block.html'

    def get_text(self, context):
        # Create Form Block
        return f"""<div>Model Create Form</div>
<form action="{{% url '{context.model_code_name}_create' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class CreateFormPage(DevelopTemplate):
    extension = '_create_form.html'
    include_extension = '_create_form_block.html'

    def get_text(self, context):
        # Create Form Page
        return f"""{{% extends "base.html" %}}
    {{% block head_title %}}{context.verbose_name}{{% endblock %}}
    {{% block content %}}
    <H1>{context['verbose_name']}</H1>
    {{% include "{context.app_name}/{context.model_code_name}{self.include_extension}" %}}
    {{% endblock content %}}
    """

class UpdateFormBlock(DevelopTemplate):
    extension = '_update_form_block.html'

    def get_text(self, context):
        # Update Form Block
        return f"""<div>Model Update Form</div>
<form action="{{% url '{context.model_code_name}_update' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class UpdateFormPage(DevelopTemplate):
    extension = '_update_form.html'
    include_extension = '_update_form_block.html'

    def get_text(self, context):
        # Update Form Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context.verbose_name}</H1>
{{% include "{context.app_name}/{context.model_code_name}_update_form_block.html" %}}
{{% endblock content %}}
"""

class CopyFormBlock(DevelopTemplate):
    extension = '_copy_form_block.html'

    def get_text(self, context):
        # Copy Form Block
        return f"""<div>Model Copy Form</div>
<form action="{{% url '{context.model_code_name}_copy' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class CopyFormPage(DevelopTemplate):
    extension = '_copy_form.html'
    include_extension = '_copy_form_block.html'

    def get_text(self, context):
        # Copy Form Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context['verbose_name']}</H1>
{{% include "{context.app_name}/{context.model_code_name}{self.include_extension}" %}}
{{% endblock content %}}
"""

class DeleteFormBlock(DevelopTemplate):
    extension = '_delete_form_block.html'
    
    def get_text(self, context):
        # Delete Form Block
        return f"""<div>Model Delete Form</div>
<form action="{{% url \'{context.model_code_name}_delete\' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class DeleteFormPage(DevelopTemplate):
    extension = '_delete_form.html'
    include_extension = '_delete_form_block.html'
    def get_text(self, context):
        return f"""{{% extends "base.html" %}}
    {{% block head_title %}}{context.verbose_name}{{% endblock %}}
    {{% block content %}}
    <H1>{context['verbose_name']}</H1>
    {{% include "{context.app_name}/{context.model_code_name}{self.include_extension}" %}}
    {{% endblock content %}}
    """

