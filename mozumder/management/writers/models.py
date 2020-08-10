import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *

class ModelWriter(Writer):
    """Need to set self.extension and get_source when subclassing
    """
    sub_directory = 'models'
    extension = '.py'

    def generate(self, context):
        # Write models.py file
        output = f"""from django.db import models
from django.utils.translation import gettext as _

# Create your models here
class {context.model.name}(models.Model):\n
"""

        field_objs = TrackedField.objects.filter(owner=context.model)
        for field_obj in field_objs:
            output += get_field(field_obj)
        output += "\n"
        return output

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

