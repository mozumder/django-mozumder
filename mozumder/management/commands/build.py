import os
import subprocess

from django.core.management.base import BaseCommand
from django.core import management

from ...models.development import TrackedApp
from ..writers import write_app

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

        apps_list = [app.name for app in app_objs]
        subprocess.run(['manage.py', 'makemigrations', *apps_list])

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

