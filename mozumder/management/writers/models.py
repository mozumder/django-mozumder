import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *

class ModelWriter(Writer):
    sub_directory = 'models'
    extension = '.py'
    def get_filename(self, context):
        # Subclass this as needed. This function defines the file name.
        return f"{context['model_code_name']}{self.extension}"

    def generate(self, context):
        # Write models.py file
        output = f"""from django.db import models
from django.utils.translation import gettext as _
from django.db.models import F

# Create your models here
class {context.model.name}(models.Model):
"""

        field_objs = TrackedField.objects.filter(owner=context.model)
        for field_obj in field_objs:
            output += get_field(field_obj)
        meta = get_meta(context.model)
        if meta:
            output += "    class Meta:\n"
            for line in meta:
                output += f"        {line}\n"
        output += "\n"
        return output

class MetaModelsWriter(Writer):
    sub_directory = 'models'
    filename = 'meta'
    extension = '.py'

    def generate(self, context):
        # Write models.py file
        output = f"""from django.db import models
from django.utils.translation import gettext as _
from django.db.models import F

# Create your models here
"""

        for model_obj in context.models:

            output += f"class {model_obj.name}(models.Model):\n"
            field_objs = TrackedField.objects.filter(owner=model_obj)
            for field_obj in field_objs:
                output += get_field(field_obj)
            meta = get_meta(model_obj)
            if meta:
                output += "    class Meta:\n"
                for line in meta:
                    output += f"        {line}\n"
            output += "\n"
        return output

# Model Meta definitions
def get_meta(model_obj):
    meta = []
    if model_obj.abstract == True:
        meta.append('abstract = True')
    if model_obj.app_label != None:
        meta.append(f"app_label = {model_obj.app_label}")
    if model_obj.base_manager_name != None:
        meta.append(f"base_manager_name = {model_obj.base_manager_name}")
    if model_obj.db_table != None:
        meta.append(f"db_table = {model_obj.db_table}")
    if model_obj.db_tablespace != None:
        meta.append(f"db_tablespace = {model_obj.db_tablespace}")
    if model_obj.default_manager_name != None:
        meta.append(f"default_manager_name = {model_obj.default_manager_name}")
    if model_obj.default_related_name != None:
        meta.append(f"default_related_name = {model_obj.default_related_name}")
    get_latest_by_items = Latest.objects.filter(latest_model=model_obj)
    if get_latest_by_items:
        get_latest_by = []
        for get_latest_by_item in get_latest_by_items:
            if get_latest_by_item.nulls_last == True:
                if get_latest_by_item.descending == True:
                    get_latest_by.append(f"F('{get_latest_by_item.latest_field.name}').desc(nulls_last=True)")
                else:
                    get_latest_by.append(f"F('{get_latest_by_item.latest_field.name}').asc(nulls_last=True)")
            else:
                if get_latest_by_item.descending == True:
                    get_latest_by.append(f"'-{get_latest_by_item.latest_field.name}'")
                else:
                    get_latest_by.append(f"'{get_latest_by_item.latest_field.name}'")
        meta.append(f"get_latest_by = [{', '.join(get_latest_by)}]")
    if model_obj.managed == True:
        meta.append('managed = True')
    if model_obj.order_with_respect_to != None:
        meta.append(f"order_with_respect_to = {model_obj.order_with_respect_to}")
    ordering_items = Ordering.objects.filter(source=model_obj)
    if ordering_items:
        ordering = []
        for ordering_item in ordering_items:
            if ordering_item.nulls_last == True:
                if ordering_item.descending == True:
                    ordering.append(f"F('{ordering_item.target_field.name}').desc(nulls_last=True)")
                else:
                    ordering.append(f"F('{ordering_item.target_field.name}').asc(nulls_last=True)")
            else:
                if ordering_item.descending == True:
                    ordering.append(f"'-{ordering_item.target_field.name}'")
                else:
                    ordering.append(f"'{ordering_item.target_field.name}'")
        meta.append(f"ordering = [{', '.join(ordering)}]")

    extra_permissions = model_obj.permissions.all()
    if extra_permissions:
        permissions = []
        for extra_permission in extra_permissions:
            permissions.append( f"({extra_permission.permission_code}, {extra_permission.human_readable_permission_name})")
            
        meta.append(f"permissions = [{', '.join(permissions)}]")

    default_permissions = [permission.permission_code for permission in model_obj.default_permissions.all()]
    if set(['add','change','delete','view']) != set(default_permissions):
        meta.append(f"default_permissions = {default_permissions}")
    if model_obj.proxy == True:
        meta.append('proxy = True')
    if model_obj.select_on_save == True:
        meta.append('select_on_save = True')
    
    if model_obj.verbose_name != '':
        meta.append(f"verbose_name = {model_obj.verbose_name}")
    if model_obj.verbose_name_plural != '':
        meta.append(f"verbose_name_plural = {model_obj.verbose_name_plural}")
    return meta

# Field definitions, separated out for reuse
def get_field(field):

    model_field_params = {}
    model_field_param_pairs = []
    if FieldTypes(field.type).label == 'ForeignKey':
        model_to = TrackedModel.objects.get(name=field.to.split('.')[-1])
        model_field_param_pairs += ["'" + field.to + "'"]
        model_field_params['on_delete'] = 'models.' + str(OnDelete(field.on_delete).label)
    if FieldTypes(field.type).label == 'ManyToManyField':
        model_to = TrackedModel.objects.get(name=field.to.split('.')[-1])
        model_field_param_pairs += ["'" + field.to + "'"]
    if snake_case_to_verbose(field.name) != field.verbose_name:
        model_field_param_pairs += [f"_('{field.verbose_name}')"]
    if field.related_name:
        model_field_params['related_name'] = "'" + field.related_name + "'"
    if field.max_length:
        model_field_params['max_length'] = field.max_length
    if field.default_bool == True:
        model_field_params['default'] = True
    if field.default_bool == False:
        model_field_params['default'] = False
    if field.default_text:
        model_field_params['default'] = "'" + field.default_text + "'"
    if field.default_smallint:
        model_field_params['default'] = field.default_smallint
    if field.auto_created == True:
        model_field_params['auto_created'] = True
    if field.serialize == False:
        model_field_params['serialize'] = False
    if field.auto_now == True:
        model_field_params['auto_now'] = True
    if field.auto_now_add == True:
        model_field_params['auto_now_add'] = True
    if field.null == True:
        model_field_params['null'] = True
    if field.blank == True:
        model_field_params['blank'] = True
    if field.db_index == True:
        model_field_params['db_index'] = True
    if field.primary_key == True:
        model_field_params['primary_key'] = True
    if field.unique == True:
        model_field_params['unique'] = True
    if field.unique_for_date == True:
        model_field_params['unique_for_date'] = True
    if field.unique_for_month == True:
        model_field_params['unique_for_month'] = True
    if field.unique_for_year == True:
        model_field_params['unique_for_year'] = True
    if FieldTypes(field.type).label == 'ImageField' or FieldTypes(field.type).label == 'FileField':
        model_field_params['upload_to'] = "''" if field.upload_to == None else field.upload_to
    model_field_param_pairs += [f'{k}={v}' for k, v in model_field_params.items()]
    
    if field.auto_created == True:
        model_text = ''
    else:
        model_text = f"    {field.name} = models.{FieldTypes(field.type).label}({', '.join(model_field_param_pairs)})\n"
    return model_text

