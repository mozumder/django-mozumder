import os
from .base import Writer
from ...models.development import *
from ..utilities.name_case import *

class AdminWriter(Writer):
    sub_directory = 'admin'
    extension = '.py'

    def generate(self, context):
        # Write admin.py file
        show_in_list_view = TrackedField.objects.filter(owner=context.model,show_in_list_view=True)
        link_in_list_view = TrackedField.objects.filter(owner=context.model,link_in_list_view=True)
        admin_readonly_field = TrackedField.objects.filter(owner=context.model,admin_readonly_field=True)
        admin_search = TrackedField.objects.filter(owner=context.model,admin_search=True)

        list_display = [field.name for field in show_in_list_view]
        list_display_links = [field.name for field in link_in_list_view]
        readonly_fields = [field.name for field in admin_readonly_field]
        search_fields = [field.name for field in admin_search]

        output = f"""from django.contrib import admin
from django.urls import reverse
from ..models import {context.model.name}
            
@admin.register({context.model.name})
class {context.model.name}Admin(admin.ModelAdmin):
"""
        if list_display or list_display_links or readonly_fields or search_fields:
            if list_display:
                output += f"    list_display={', '.join(map(str, [list_display]))}\n"
            if list_display_links:
                output += f"    list_display_links={', '.join(map(str, [list_display_links]))}\n"
            if readonly_fields:
                output += f"    readonly_fields={', '.join(map(str, [readonly_fields]))}\n"
            if search_fields:
                output += f"    search_fields={', '.join(map(str, [search_fields]))}\n"
            output += '\n'
        else:
            output += '    pass\n'

        return output
