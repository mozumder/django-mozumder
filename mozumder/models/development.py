from django.db import models
from .. import FieldTypes, OnDelete, ConstraintType, IPAddressProtocol
from django.contrib.auth.models import Permission

# Create your models here.

class TrackedApp(models.Model):
    name = models.CharField(max_length=80)
    def __str__(self):
        return self.name

class Choices(models.Model):
    value = models.CharField(max_length=80)
    label = models.CharField(max_length=80)

class TrackedField(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey('TrackedModel',on_delete=models.CASCADE)
    type = models.CharField(
        max_length=2,
        choices=FieldTypes.choices,
    )
    verbose_name = models.CharField(max_length=80, null=True, blank=True)

    auto_created = models.BooleanField(null=True, blank=True)
    serialize = models.BooleanField(null=True, blank=True)
    primary_key = models.BooleanField(null=True, blank=True)

    null = models.BooleanField(null=True, blank=True)
    blank = models.BooleanField(null=True, blank=True)
    
    db_index = models.BooleanField(null=True, blank=True)
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
    default_bigint = models.BigIntegerField(null=True, blank=True)
    default_int = models.IntegerField(null=True, blank=True)
    default_posint = models.PositiveIntegerField(null=True, blank=True)
    default_possmallint = models.PositiveSmallIntegerField(null=True, blank=True)
    default_datetime = models.DateTimeField(null=True, blank=True)
    default_float = models.FloatField(null=True, blank=True)
    default_decimal = models.DecimalField(max_digits=18, decimal_places=18, null=True, blank=True)

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
    decimal_places = models.SmallIntegerField(null=True, blank=True)

    #Field: FileField
    upload_to = models.CharField(max_length=255,null=True, blank=True)

    #Field: GenericIPAddressField
    protocol = models.CharField(max_length=2, choices=IPAddressProtocol.choices, null=True, blank=True)
    unpack_ipv4 = models.BooleanField(null=True, blank=True)

    #Field: SlugField
    sllow_unicode = models.BooleanField(null=True, blank=True)
    def __str__(self):
        return self.name

class Index(models.Model):
    fields = models.ManyToManyField(TrackedField)
    name = models.CharField(max_length=80, null=True, blank=True)
    def __str__(self):
        return self.name

class Contraint(models.Model):
    type = models.CharField(max_length=2, choices=ConstraintType.choices)
    unique_fields = models.ManyToManyField('TrackedField')
    check_function = models.CharField(max_length=512, null=True, blank=True)
    name = models.CharField(max_length=80, null=True, blank=True)

class Mixin(models.Model):
    name = models.CharField(max_length=80)
    code = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

class Arg(models.Model):
    name = models.CharField(max_length=80, null=True, blank=True)
    value = models.CharField(max_length=80, null=True, blank=True)
    def __str__(self):
        return self.name

class Function(models.Model):
    name = models.CharField(max_length=80)
    args = models.ManyToManyField(TrackedField, related_name='function_args')
    kwargs = models.ManyToManyField(TrackedField, related_name='function_kwargs')
    code = models.TextField(null=True, blank=True)

class Latest(models.Model):
    latest_field = models.ForeignKey('TrackedField', on_delete=models.CASCADE)
    latest_model = models.ForeignKey('TrackedModel', on_delete=models.CASCADE)
    descending = models.BooleanField(default=False)

class Ordering(models.Model):
    target_field = models.ForeignKey('TrackedField', on_delete=models.CASCADE)
    source = models.ForeignKey('TrackedModel', related_name='source_ordering_model', on_delete=models.CASCADE)
    descending = models.BooleanField(default=False)

class ExtraPermission(models.Model):
    name = models.CharField(max_length=80, null=True, blank=True)
    value = models.CharField(max_length=80, null=True, blank=True)
    def __str__(self):
        return self.name

class TrackedModel(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey('TrackedApp',on_delete=models.CASCADE)
    verbose_name = models.CharField(max_length=80)
    verbose_name_plural = models.CharField(max_length=80)
    abstract = models.BooleanField(null=True, blank=True)
    app_label = models.CharField(max_length=80, null=True, blank=True)
    base_manager_name = models.CharField(max_length=80, null=True, blank=True)
    db_table = models.CharField(max_length=80, null=True, blank=True)
    db_tablespace = models.CharField(max_length=80, null=True, blank=True)
    default_manager_name = models.CharField(max_length=80, null=True, blank=True)
    default_related_name = models.CharField(max_length=80, null=True, blank=True)
    get_latest_by = models.ManyToManyField('TrackedField', related_name='latest_fields', through='latest', through_fields=('latest_model','latest_field'))
    managed = models.BooleanField(null=True, blank=True)
    order_with_respect_to = models.ForeignKey('TrackedField', related_name='ordered_with_respect_to_field', on_delete=models.SET_NULL, null=True, blank=True)
    ordering = models.ManyToManyField('TrackedField',through='ordering',related_name='ordering_fields', through_fields=('source','target_field'))
    permissions = models.ManyToManyField('ExtraPermission')
    default_permissions = models.ManyToManyField(Permission)
    proxy = models.BooleanField(null=True, blank=True)

    mixins = models.ManyToManyField(Mixin)
    function = models.ManyToManyField(Function)
    def __str__(self):
        return self.name
