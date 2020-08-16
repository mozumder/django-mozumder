import os
from dotmap import DotMap
from ..utilities.name_case import *
from .base import Writer
from ...models.development import *

class URLsWriter(Writer):
    sub_directory = 'urls'
    filename = '__init__'
    extension = '.py'

    def update(self, context_dict):
        # Write urls.py file

        context = DotMap(context_dict)

        # Edit base URLs py
        urls_file = self.get_file(context)

        f = open(urls_file, "r")
        output = ''
        state = 'file'
        for line in f.readlines():
            if state == 'file':
                if line.startswith('urlpatterns = [\n'):
                    state = 'urlpatterns'
                elif line.startswith("from django.urls import path"):
                    view_objs = TrackedView.objects.filter(model=context.model, api_url=False)
                    views_imports_list = ', '.join([str(view_obj.name) for view_obj in view_objs])
                    line += f"from ..views import {views_imports_list}\n"
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    view_objs = TrackedView.objects.filter(model=context.model, api_url=False)
                    for view_obj in view_objs:
                        if view_obj.class_based_view == True:
                            output += f"    path({view_obj.url}, {view_obj.name}.as_view(), name={view_obj.url_name}),\n"
                        else:
                            output += f"    path({view_obj.url}, {view_obj.name}, name={view_obj.url_name}),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()

class APIURLsWriter(URLsWriter):
    def get_filepath(self, context):
        # Add a sub-sub directory for API urls.
        return os.path.join(os.getcwd(),context['app'].name,self.sub_directory, 'api')

    def update(self, context_dict):

        context = DotMap(context_dict)

        # Edit base URLs py
        urls_file = self.get_file(context)

        f = open(urls_file, "r")
        output = ''
        state = 'file'
        for line in f.readlines():
            if state == 'file':
                if line.startswith('urlpatterns = [\n'):
                    state = 'urlpatterns'
                elif line.startswith("from django.urls import path"):
                    view_objs = TrackedView.objects.filter(model=context.model, api_url=True)
                    views_imports_list = ', '.join([str(view_obj.name) for view_obj in view_objs])
                    line += f"from ...views import {views_imports_list}\n"
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field
                    view_objs = TrackedView.objects.filter(model=context.model, api_url=True)
                    for view_obj in view_objs:
                        if view_obj.class_based_view == True:
                            output += f"    path({view_obj.url}, {view_obj.name}.as_view(), name={view_obj.url_name}),\n"
                        else:
                            output += f"    path({view_obj.url}, {view_obj.name}, name={view_obj.url_name}),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()
