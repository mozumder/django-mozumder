import os
from django.core.management.base import BaseCommand
from dotmap import DotMap
import mozumder
from ...models.development import *
from ..utilities.name_case import *

class Command(BaseCommand):

    help = 'Build Mozumder apps.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'apps',
            nargs='*',
            action='store',
            help='Mozumder apps to build. If none given, build all mozumder apps',
            )
    def handle(self, *args, **options):

        apps = options['apps']

        if apps == []:
            app_objs = TrackedApp.objects.all()
        else:
            app_objs = TrackedApp.objects.filter(name__in=apps)


        for app_obj in app_objs:
            write_app(app_obj)
            enable_app(app_obj)

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
                else:
                    print (f"Created directory {path}")
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
            output = get_model(model_obj)
            file = os.path.join(target_root,'models',model_obj.name.lower()+'.py')
            print(f'Writing file: {file}')
            f = open(file, "w")
            f.write(output)
            f.close()
            imports += f'from .{model_obj.name.lower()} import {model_obj.name}\n'

        model_package_file = os.path.join(target_root,'models','__init__.py')
        p = open(model_package_file, "w")
        p.write(imports)
        p.close()


def get_model(model_obj):
    output = f"""from django.db import models
from django.utils.translation import gettext as _

# Create your models here
class {model_obj.name}(models.Model):\n
"""

    field_objs = TrackedField.objects.filter(owner=model_obj)
    for field_obj in field_objs:
        output += get_field(field_obj)
    output += "\n"
    return output

def get_field(field):

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
    
    return f"    {field.name} = models.{FieldTypes(field.type).label}({', '.join(field_param_pairs)})\n"


def enable_app(app_obj):
    app_name = app_obj.name
    
    project_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
    project_name, project_settings_name = project_settings.split('.')

    path = os.path.join(os.getcwd(),app_name)
    access_rights = 0o755
            
    # Edit project URLs py
    print('Editing urls.py')
    urls_file = os.path.join(os.getcwd(),project_name,'urls.py')

    f = open(urls_file, "r")
    output = ''
    state = 'file'
    for line in f.readlines():
        if state == 'file':
            if line == 'urlpatterns = [\n':
                state = 'urlpatterns'
        elif state == 'urlpatterns':
            if line == ']\n':
                output += f"    path('{app_name}/', include('{app_name}.urls')),\n"
                output += f"    path('api/{app_name}/', include('{app_name}.urls.api')),\n"
                state = 'file'
        output += line
    f.close()
    f = open(urls_file, "w")
    f.write(output)
    f.close()

    # Edit settings.py
    print('Editing settings.py')
    settings_file = os.path.join(os.getcwd(),project_name,project_settings_name+'.py')

    f = open(settings_file, "r")
    output = ''
    state = 'file'
    for line in f.readlines():
        if state == 'file':
            if line == 'INSTALLED_APPS = [\n':
                state = 'INSTALLED_APPS'
        elif state == 'INSTALLED_APPS':
            if line == ']\n':
                output += f"    '{app_name}',\n"
                state = 'file'
        output += line
    f.close()
    f = open(settings_file, "w")
    f.write(output)
    f.close()

    #Add model to Homepage
    models_html_file = os.path.join(os.getcwd(),project_name,'templates','models.html')

    f = open(models_html_file, "r")
    output = ''
    state = 'main'
    for line in f.readlines():
        if state == 'main':
            if line.startswith("<ul>"):
                state = 'list'
        elif state == 'list':
            if line.startswith("</ul>"):
                output += f"""<li>{app_name}\n<ul>\n{{% include "{app_name}/models.html" %}}\n</ul>\n</li>\n"""
                state = 'main'
            elif line.startswith("<li>"):
                state = 'app'
        elif state == 'app':
            if line.startswith("<ul>"):
                state = 'model'
            elif line.startswith("</li>"):
                state = 'list'
        elif state == 'model':
            if line.startswith("</ul>"):
                state = 'app'
        output += line
    f.close()
    
    f = open(models_html_file, "w")
    f.write(output)
    f.close()

