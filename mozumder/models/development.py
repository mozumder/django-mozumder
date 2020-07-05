from django.db import models
from .. import FieldTypes, OnDelete

# Create your models here.

class TrackedApp(models.Model):
    name = models.CharField(max_length=80)

class TrackedModel(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(TrackedApp,on_delete=models.CASCADE)
    verbose_name = models.CharField(max_length=80)
    verbose_name_plural = models.CharField(max_length=80)

class Choices(models.Model):
    value = models.CharField(max_length=80)
    label = models.CharField(max_length=80)

class TrackedField(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(TrackedModel,on_delete=models.CASCADE)
    type = models.CharField(
        max_length=2,
        choices=FieldTypes.choices,
    )
    verbose_name = models.CharField(max_length=80, null=True, blank=True)

    null = models.BooleanField(null=True, blank=True)
    blank = models.BooleanField(null=True, blank=True)
    db_column = models.CharField(max_length=80, null=True, blank=True)
    db_index = models.BooleanField(null=True, blank=True)
    default = models.CharField(max_length=80, null=True, blank=True)
    editable = models.BooleanField(null=True, blank=True)

    admin_list_display = models.BooleanField(null=True, blank=True)
    admin_list_display_links = models.BooleanField(null=True, blank=True)
    admin_readonly_field = models.BooleanField(null=True, blank=True)
    admin_search = models.BooleanField(null=True, blank=True)

    max_length = models.BooleanField(null=True, blank=True)

    #Field: ForeignKey
    choices = models.ManyToManyField(Choices)
    on_delete = models.CharField(
        max_length=2,
        choices=OnDelete.choices,
        null=True, blank=True
    )
    related_name = models.CharField(max_length=80, null=True, blank=True)
    related_query_name = models.CharField(max_length=80, null=True, blank=True)
    # limit_choices_to

    #Field: ManyToManyField
    symmetrical = models.BooleanField(null=True, blank=True)
    through = models.CharField(max_length=80, null=True, blank=True)
    through_fields_source = models.CharField(max_length=80, null=True, blank=True)
    through_fields_target = models.CharField(max_length=80, null=True, blank=True)
    db_table = models.CharField(max_length=80, null=True, blank=True)
    db_constraint = models.BooleanField(null=True, blank=True)
    swappable = models.BooleanField(null=True, blank=True)

    #Field: OneToOneField
    parent_link = models.BooleanField(null=True, blank=True)
