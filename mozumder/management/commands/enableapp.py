import os
from shutil import copyfile

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder

class Command(BaseCommand):

    help = 'Modify Django Settings and URLs to enable an app.'
    
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
