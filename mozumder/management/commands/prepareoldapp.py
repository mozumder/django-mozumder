import os
from shutil import copyfile

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder

class Command(BaseCommand):

    help = 'Modify newly created Django app to add URL and template directories.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            'name',
            action='store',
            help='App name',
            )
            
    def handle(self, *args, **options):

        app_name = options['name']

        project_settings = os.environ.get('DJANGO_SETTINGS_MODULE')
        project_name, project_settings_name = project_settings.split('.')

        path = os.path.join(os.getcwd(),app_name)
        access_rights = 0o755

        source_root = os.path.join(mozumder.__file__[:-12], 'include','old_app_template')
        source_root_length = len(source_root)

        target_root = os.path.join(os.getcwd(),app_name)

        for root, dirs, files in os.walk(source_root):
            # Process files from source templates directory and install
            # them in the new project directory
            sub_dir = root[source_root_length+1:]
            if sub_dir == 'app_name':
                sub_dir = app_name
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
                
        # Edit URLs py
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
