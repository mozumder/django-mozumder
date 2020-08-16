import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *
from ... import ViewBaseClass, DefaultMixins

class ViewWriter(Writer):
    sub_directory = 'views'
    extension = '.py'

    def get_filename(self, context):
        # Subclass this as needed. This function defines the file name.
        return f"{context['model_code_name']}{self.extension}"

    def generate(self, context):
        # Write views.py file

        view_code = ''
        base_classes = {}
        
        view_objs = TrackedView.objects.filter(model=context.model)
        for view_obj in view_objs:
            if view_obj.class_based_view == True:
                base_class = ViewBaseClass(view_obj.base_class).label
                base_classes[base_class] = ''
                view_code += f"class {view_obj.name}({base_class}):\n"
                if view_obj.model:
                    view_code += f"    model = {context.model.name}\n"
                fields = view_obj.fields.all()
                if fields:
                    form_fields = [field.name for field in fields]
                    view_code += f"    fields = {form_fields}\n"
                if view_obj.template_name_suffix:
                    view_code += f"    template_name_suffix = {view_obj.template_name_suffix}\n"
                if view_obj.success_url:
                    view_code += f"    success_url = {view_obj.success_url}\n"
                view_code += "\n"
            else:
                view_code += f"""def {view_obj.name}():
    pass

"""

        output = "from django.urls import reverse_lazy\n"
        if base_classes.keys():
            generic_views_imports = ', '.join([str(k) for k in base_classes.keys()])
            output += f"from django.views.generic import {generic_views_imports}\n"
        if hasattr(context,'model'):
            output += f"from ..models import {context.model.name}\n"
        output += view_code

        return output
