import os
import mozumder
from ...models.development import *
from ..utilities.name_case import *

def write_app(app_obj):
        app_name = app_obj.name
        access_rights = 0o755
        source_root = os.path.join(mozumder.__file__[:-12], 'include','app_template')
        source_root_length = len(source_root)

        target_root = os.path.join(os.getcwd(),app_name)
        try:
            os.mkdir(target_root, access_rights)
        except OSError:
            print (f"Creation of app directory {target_root} failed")
        else:
            print (f"Created app directory {target_root}")

        for root, dirs, files in os.walk(source_root):
            # Process files from source templates directory and install
            # them in the new app directory
            sub_dir = root[source_root_length+1:].replace('app_name',app_name)
            target_path = os.path.join(target_root, sub_dir)
            for name in dirs:
                if name == 'app_name':
                    name = app_name
                path = os.path.join(target_path, name)
                try:
                    os.mkdir(path,mode=0o755)
                except OSError:
                    print (f"Creation of the directory {path} failed")
            for name in files:
                source_filename = os.path.join(root, name)
                if name[-4:] == '-tpl':
                    f = open(source_filename, "r")
                    fstring_from_file = 'f"""'+f.read()+'"""'
                    f.close()
                    # Evaluate F-String
                    compiled_fstring = compile(fstring_from_file, source_filename, 'eval')
                    formatted_output = eval(compiled_fstring)
                    name = name[:-4]
                    target_filename = os.path.join(target_path, name)
                    # Write evaluated F-String
                    f = open(target_filename, "w")
                    f.write(formatted_output)
                    f.close()
                    status = os.stat(source_filename).st_mode & 0o777
                    os.chmod(target_filename,status)
                else:
                    target_filename = os.path.join(target_path, name)
                    copyfile(source_filename, target_filename)

        model_objs = TrackedModel.objects.filter(owner=app_obj)
        
        imports = ''

        for model_obj in model_objs:
            model_output = get_model(model_obj)
            file = os.path.join(target_root,'models',model_obj.name.lower()+'.py')
            print(f'Writing model file: {file}')
            f = open(file, "w")
            f.write(model_output)
            f.close()
            imports += f'from .{model_obj.name.lower()} import {model_obj.name}\n'
        model_package_file = os.path.join(target_root,'models','__init__.py')
        f = open(model_package_file, "w")
        f.write(imports)
        f.close()

def get_model(model_obj):
    model_output = f"""from django.db import models
from django.utils.translation import gettext as _

# Create your models here
class {model_obj.name}(models.Model):\n
"""

    migration_output = f"""        migrations.CreateModel(
            name='{model_obj.name}',
            fields=[
"""
    field_objs = TrackedField.objects.filter(owner=model_obj)
    for field_obj in field_objs:
        model_output += get_field(field_obj)
    model_output += "\n"
    return model_output

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

