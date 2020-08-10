import os
from dotmap import DotMap
from ..utilities.name_case import *
from .base import Writer
from ...models.development import *

class URLsWriter(Writer):
    sub_directory = 'urls'
    extension = '.py'
    
    def get_filename(self, context):
        # Subclass this as needed. This function defines the file name.
        return f"__init__{self.extension}"

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
                    line += f"""from ..views import {context.model.name}ListView, \\
    {context.model.name}AddView, {context.model.name}DetailView, {context.model.name}UpdateView, \\
    {context.model.name}CopyView, {context.model.name}DeleteView, search_{context.model_code_name}
"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{context.model_code_name}/', {context.model.name}ListView.as_view(), name='{context.model_code_name}_list'),\n"
                    output += f"    path('{context.model_code_name}/add', {context.model.name}AddView.as_view(), name='{context.model_code_name}_add'),\n"
                    output += f"    path('{context.model_code_name}/<int:pk>', {context.model.name}DetailView.as_view(), name='{context.model_code_name}_detail'),\n"
                    output += f"    path('{context.model_code_name}/<int:pk>/update', {context.model.name}UpdateView.as_view(), name='{context.model_code_name}_update'),\n"
                    output += f"    path('{context.model_code_name}/<int:pk>/copy', {context.model.name}CopyView.as_view(), name='{context.model_code_name}_copy'),\n"
                    output += f"    path('{context.model_code_name}/<int:pk>/delete', {context.model.name}DeleteView.as_view(), name='{context.model_code_name}_delete'),\n"
                    output += f"    path('search/{context.model_code_name}', search_{context.model_code_name}, name='search_{context.model_code_name}'),\n"
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
                    line += f"""from ...views import {context.model.name}JSONListView, \\
    {context.model.name}JSONDetailView, json_search_{context.model_code_name}
"""
            elif state == 'urlpatterns':
                if line == ']\n':
                    # GET: Read All, DELETE: Delete All, POST: Add, PATCH: Update All Field
                    output += f"    path('{context.model_code_name}/', {context.model.name}JSONListView.as_view(), name='json_{context.model_code_name}_list'),\n"
                    # GET: Read One, DELETE: Delete One, POST: Copy, PUT: Update Fields, PATCH: Update Field
                    output += f"    path('{context.model_code_name}/<int:pk>', {context.model.name}JSONDetailView.as_view(), name='json_{context.model_code_name}_detail'),\n"
                    output += f"    path('search/{context.model_code_name}', json_search_{context.model_code_name}, name='search_{context.model_code_name}'),\n"
                    state = 'file'
            output += line
        f.close()
        f = open(urls_file, "w")
        f.write(output)
        f.close()
