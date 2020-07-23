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
    
    db_index = models.BooleanField(null=True, blank=True)
    primary_key = models.BooleanField(null=True, blank=True)
    db_column = models.CharField(max_length=80, null=True, blank=True)
    db_tablespace = models.CharField(max_length=80, null=True, blank=True)

    editable = models.BooleanField(null=True, blank=True)

    show_in_detail_view = models.BooleanField(null=True, blank=True)
    show_in_list_view = models.BooleanField(null=True, blank=True)
    link_in_list_view = models.BooleanField(null=True, blank=True)

    admin_readonly_field = models.BooleanField(null=True, blank=True)
    admin_search = models.BooleanField(null=True, blank=True)

    unique = models.BooleanField(null=True, blank=True)
    unique_for_date = models.BooleanField(null=True, blank=True)
    unique_for_month = models.BooleanField(null=True, blank=True)
    unique_for_year = models.BooleanField(null=True, blank=True)

    default_bool = models.BooleanField(null=True, blank=True)
    default_text = models.TextField(null=True, blank=True)
    default_smallint = models.SmallIntegerField(null=True, blank=True)
    default_bigint = models.SmallIntegerField(null=True, blank=True)
    default_datetime = models.DateTimeField(null=True, blank=True)

    choices = models.ManyToManyField(Choices)

    #Field: CharField
    max_length = models.SmallIntegerField(null=True, blank=True)

    #Field: ForeignKey
    to = models.CharField(max_length=80, null=True, blank=True)
    on_delete = models.CharField(
        max_length=2,
        choices=OnDelete.choices,
        null=True, blank=True
    )
    related_name = models.CharField(max_length=80, null=True, blank=True)
    related_query_name = models.CharField(max_length=80, null=True, blank=True)
    limit_choices_to = models.TextField(null=True, blank=True)
    to_field = models.CharField(max_length=80, null=True, blank=True)

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
    
    #Field: DateField, DateTimeField
    auto_now = models.BooleanField(null=True, blank=True)
    auto_now_add = models.BooleanField(null=True, blank=True)

    #Field: DecimalField
    max_digits = models.SmallIntegerField(null=True, blank=True)

    #Field: FileField
    upload_to = models.CharField(max_length=255,null=True, blank=True)
