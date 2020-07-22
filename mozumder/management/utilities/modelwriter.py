## Method 1
import inspect

class magic_fstring_function:
    def __init__(self, payload):
        self.payload = payload
    def __str__(self):
        vars = inspect.currentframe().f_back.f_globals.copy()
        vars.update(inspect.currentframe().f_back.f_locals)
        return self.payload.format(**vars)

template = "The current name is {name}"

template_a = magic_fstring_function(template)

# use it inside a function to demonstrate it gets the scoping right
def new_scope():
    names = ["foo", "bar"]
    for name in names:
        print(template_a)

new_scope()
# The current name is foo
# The current name is bar

## Method 2
template_a = lambda: f"The current name is {name}"
names = ["foo", "bar"]
for name in names:
    print (template_a())


class Element:

        text = f"""{{% extends "base.html" %}}
    {{% block head_title %}}{verbose_name}{{% endblock %}}
    {{% block content %}}
    <H1>{ verbose_name }</H1>
    {{% include "{self.context['app_name']}/{self.context['model_code_name']}{self.context['include_extension']}" %}}
    {{% endblock content %}}
    """
    
    def __init__(app_name, text,context={},template_dir='templates'):
        self.text = text
        self.context = context
        self.template_dir = template_dir

    def write(extension):

        filename = os.path.join(os.getcwd(),self.context['app_name'],self.context['template_dir'],self.context['app_name'],f"{self.context['model_code_name']}{self.context['extension']}')
        f = open(filename, "w")
        f.write(self.text)
        f.close()



    def write():
        # Read & modify models.py file
        models_file = os.path.join(os.getcwd(),app_name,'models.py')
        f = open(models_file, "r")
        output = ''
        has_reverse = False
        for line in f.readlines():
            if line.startswith('# Create your models here.'):
                if has_reverse == False:
                    output += f"from django.shortcuts import reverse\n"
            elif line.startswith('from django.shortcuts import reverse'):
                has_reverse = True
            output += line
        output += model
        f.close()
        # Write models.py file
        f = open(models_file, "w")
        f.write(output)
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
                file += f"""from django.urls import reverse
from .models import {model_name}
"""
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

        # Model Detail Block
        field_ul = ''
        for field in detail_display:
            field_ul += f"<li>{{{{{model_code_name}.{field}}}}}</li>"

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


        # Create Form Block
        create_form_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_create_form_block.html')
        f = open(create_form_block_file, "w")
        f.write(f"""<div>Model Add Form</div>
<form action="{{% url '{model_code_name}_add' %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>""")
        f.close()

        # Create Form Page
        create_form_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_create_form.html')
        f = open(create_form_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name }</H1>
{{% include "{app_name}/{model_code_name}_create_form_block.html" %}}
{{% endblock content %}}
""")
        f.close()


        # Update Form Block
        update_form_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_update_form_block.html')
        f = open(update_form_block_file, "w")
        f.write(f"""<div>Model Update Form</div>
<form action="{{% url '{model_code_name}_update' {model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>""")
        f.close()

        # Update Form Page
        update_form_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_update_form.html')
        f = open(update_form_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name }</H1>
{{% include "{app_name}/{model_code_name}_update_form_block.html" %}}
{{% endblock content %}}
""")
        f.close()


        # Copy Form Block
        copy_form_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_copy_form_block.html')
        f = open(copy_form_block_file, "w")
        f.write(f"""<div>Model Copy Form</div>
<form action="{{% url '{model_code_name}_copy' {model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>""")
        f.close()

        # Copy Form Page
        copy_form_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_copy_form.html')
        f = open(copy_form_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name }</H1>
{{% include "{app_name}/{model_code_name}_copy_form_block.html" %}}
{{% endblock content %}}
""")
        f.close()


        # Delete Form Block
        delete_form_block_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_delete_form_block.html')
        f = open(delete_form_block_file, "w")
        f.write(f"""<div>Model Delete Form</div>
<form action="{{% url '{model_code_name}_delete' {model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>""")
        f.close()

        # Delete Form Page
        delete_form_page_file = os.path.join(os.getcwd(),app_name,'templates',app_name,f'{model_code_name}_delete_form.html')
        f = open(delete_form_page_file, "w")
        f.write(f"""{{% extends "base.html" %}}
{{% block head_title %}}{verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ verbose_name }</H1>
{{% include "{app_name}/{model_code_name}_delete_form_block.html" %}}
{{% endblock content %}}
""")
        f.close()

