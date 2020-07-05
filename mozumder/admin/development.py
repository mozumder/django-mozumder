from django.contrib import admin

from ..models import TrackedApp, TrackedModel, TrackedField

@admin.register(TrackedApp)
class TrackedAppAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]

@admin.register(TrackedModel)
class TrackedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']

@admin.register(TrackedField)
class TrackedFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']

