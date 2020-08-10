import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *

class TemplateWriter(Writer):
    sub_directory = 'templates'

    def get_filepath(self, context):
        # Subclass this as needed. This function defines the file path.
        return os.path.join(os.getcwd(),context['app'].name,self.sub_directory,context['app'].name)

class ModelListBlock(TemplateWriter):
    extension = '_list_block.html'

    def generate(self, context):
        # Model List Block
        header_row = ''
        row = ''
        list_fields = TrackedField.objects.filter(owner=context.model,show_in_list_view=True)
        header_row += f'<th>ID</th>'
        row += f"""<td><a href="{{% url '{context.model_code_name}_detail' instance.id %}}">{{{{instance.id}}}}</a></td>"""
        for field in list_fields:
            header_row += f'<th>{field.name}</th>'
            if field.link_in_list_view==False:
                row += f"""<td>{{{{instance.{field.name}}}}}</td>"""
            else:
                row += f"""<td><a href="{{% url '{context.model_code_name}_detail' instance.id %}}">{{{{instance.{field.name}}}}}</a></td>"""
        header_row += '<th></th><th></th><th></th>'
        row += f"""<td><a href="{{% url '{context.model_code_name}_copy' instance.id %}}">Copy</a></td><td><a href="{{% url '{context.model_code_name}_update' instance.id %}}">Edit</a></td><td><a href="{{% url '{context.model_code_name}_delete' instance.id %}}">Delete</a></td>"""
        return f"""<table>
<tr>{header_row}</tr>
{{% for instance in object_list %}}
<tr>{ row }</tr>
{{% endfor %}}
</table>"""

class ModelListPage(TemplateWriter):
    extension = '_list.html'

    def generate(self, context):
        # Model List Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name_plural}{{% endblock %}}
{{% block content %}}
<H1>{ context.model.verbose_name_plural }</H1>
{{% include "{context.app.name}/{context.model_code_name}_list_block.html" %}}
{{% endblock content %}}
"""

class ModelDetailBlock(TemplateWriter):
    extension = '_detail_block.html'

    def generate(self, context):
        # Model Detail Block
        field_ul = ''
        fields = TrackedField.objects.filter(owner=context.model,show_in_detail_view=True)
        for field in fields:
            field_ul += f"<li>{{{{{context.model_code_name}.{field.name}}}}}</li>"

        return f'<div>Model Detail</div>\n<ul>{field_ul}</ul>'

class ModelDetailPage(TemplateWriter):
    extension = '_detail.html'

    def generate(self, context):
        # Model Detail Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{ context.model.verbose_name }</H1>
{{% include "{context.app.name}/{context.model_code_name}_detail_block.html" %}}
{{% endblock content %}}
"""

class UpdateModelsListBlock(TemplateWriter):
    extension = '_update_list_block.html'

    def generate(self, context):
        # Add model to app's models list HTML
        return f"""<li><a href="{{% url '{context.model_code_name}_list' %}}">{context.model.verbose_name}</a> <a href="{{% url '{context.model_code_name}_create' %}}">Add</a></li>"""

class CreateFormBlock(TemplateWriter):
    extension = '_create_form_block.html'

    def generate(self, context):
        # Create Form Block
        return f"""<div>Model Create Form</div>
<form action="{{% url '{context.model_code_name}_create' %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class CreateFormPage(TemplateWriter):
    extension = '_create_form.html'
    include_extension = '_create_form_block.html'

    def generate(self, context):
        # Create Form Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context.model.verbose_name}</H1>
{{% include "{context.app.name}/{context.model_code_name}{self.include_extension}" %}}
{{% endblock content %}}
"""

class UpdateFormBlock(TemplateWriter):
    extension = '_update_form_block.html'

    def generate(self, context):
        # Update Form Block
        return f"""<div>Model Update Form</div>
<form action="{{% url '{context.model_code_name}_update' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class UpdateFormPage(TemplateWriter):
    extension = '_update_form.html'
    include_extension = '_update_form_block.html'

    def generate(self, context):
        # Update Form Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context.model.verbose_name}</H1>
{{% include "{context.app.name}/{context.model_code_name}_update_form_block.html" %}}
{{% endblock content %}}
"""

class CopyFormBlock(TemplateWriter):
    extension = '_copy_form_block.html'

    def generate(self, context):
        # Copy Form Block
        return f"""<div>Model Copy Form</div>
<form action="{{% url '{context.model_code_name}_copy' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class CopyFormPage(TemplateWriter):
    extension = '_copy_form.html'
    include_extension = '_copy_form_block.html'

    def generate(self, context):
        # Copy Form Page
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context.model.verbose_name}</H1>
{{% include "{context.app.name}/{context.model_code_name}{self.include_extension}" %}}
{{% endblock content %}}
"""

class DeleteFormBlock(TemplateWriter):
    extension = '_delete_form_block.html'
    
    def generate(self, context):
        # Delete Form Block
        return f"""<div>Model Delete Form</div>
<form action="{{% url \'{context.model_code_name}_delete\' {context.model_code_name}.id %}}" method="post">
    {{% csrf_token %}}
    {{{{ form }}}}
    <input type="submit" value="Submit">
</form>"""

class DeleteFormPage(TemplateWriter):
    extension = '_delete_form.html'
    include_extension = '_delete_form_block.html'
    
    def generate(self, context):
        return f"""{{% extends "base.html" %}}
{{% block head_title %}}{context.model.verbose_name}{{% endblock %}}
{{% block content %}}
<H1>{context.model.verbose_name}</H1>
{{% include "{context.app.name}/{context.model_code_name}{self.include_extension}" %}}
{{% endblock content %}}
"""


class ModelsBlock(TemplateWriter):
    filename = 'models'
    extension = '.html'
    def get_filename(self, context):
        # Subclass this as needed. This function defines the file name.
        return f"{self.filename}{self.extension}"

    def generate(self, context):
        # Models Block
        models = TrackedModel.objects.filter(owner=context.app)
        output = ''
        for model in models:
            model_code_name = CamelCase_to_snake_case(model.name)
            output += f"""<li><a href="{{% url '{model_code_name}_list' %}}">{model.name}</a><a href="{{% url '{model_code_name}_create' %}}">Add</a></li>"""
        return output
