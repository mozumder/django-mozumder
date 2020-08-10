import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *

class ViewWriter(Writer):
    sub_directory = 'views'
    extension = '.py'

    def generate(self, context):
        # Write views.py file
        editable_fields = TrackedField.objects.filter(owner=context.model,editable=True)
        form_fields = [field.name for field in editable_fields]
        
        return f"""from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView, \\
    UpdateView, DeleteView
from ..models import {context.model.name}

class {context.model.name}DetailView(DetailView):
    model = {context.model.name}

class {context.model.name}ListView(ListView):
    model = {context.model.name}

class {context.model.name}CreateView(CreateView):
    model = {context.model.name}
    fields = {form_fields}
    template_name_suffix = '_create_form'

class {context.model.name}CopyView(UpdateView):
    model = {context.model.name}
    fields = {form_fields}
    template_name_suffix = '_copy_form'

class {context.model.name}UpdateView(UpdateView):
    model = {context.model.name}
    fields = {form_fields}
    template_name_suffix = '_update_form'

class {context.model.name}DeleteView(DeleteView):
    model = {context.model.name}
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('{context.model_code_name}_list')

def search_{context.model_code_name}():
    pass

class {context.model.name}JSONDetailView(DetailView):
    model = {context.model.name}

class {context.model.name}JSONListView(ListView):
    model = {context.model.name}

def json_search_{context.model_code_name}():
    pass
"""
