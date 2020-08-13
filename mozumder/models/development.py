from django.db import models
from .. import FieldTypes, OnDelete, ConstraintType, IPAddressProtocol, ViewBaseClass, DefaultMixins
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

class Arg(models.Model):
    name = models.CharField(max_length=80, null=True, blank=True)
    value = models.CharField(max_length=80, null=True, blank=True)
    def __str__(self):
        return self.name

class Method(models.Model):
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

    mixins = models.ManyToManyField('Mixin')
    methods = models.ManyToManyField('Method')
    def __str__(self):
        return self.name

class TrackedView(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey('TrackedApp', on_delete=models.CASCADE)
    class_based_view = models.BooleanField(null=True, blank=True)
    base_class = models.CharField(
        max_length=2,
        choices=ViewBaseClass.choices,
    )
    url = models.CharField(max_length=250)
    url_name = models.CharField(max_length=250)
    api_url = models.BooleanField(default=False)

    mixins = models.ManyToManyField('Mixin')
    methods = models.ManyToManyField('Method')

    model = models.ForeignKey('TrackedModel',on_delete=models.CASCADE, null=True, blank=True)
    
    # Redirect View
    url = models.CharField(max_length=250, null=True, blank=True)
    pattern = models.CharField(max_length=250, null=True, blank=True)
    permanent = models.BooleanField(null=True, blank=True)
    query_string = models.BooleanField(null=True, blank=True)

    # Create/Update View
    object = models.CharField(max_length=250, null=True, blank=True)
    success_url = models.CharField(max_length=250, null=True, blank=True)

    # Context Mixin
    extra_context = models.TextField(null=True, blank=True)
    
    # Template Response mixin
    template_name = models.CharField(max_length=250, null=True, blank=True)
    template_engine = models.CharField(max_length=250, null=True, blank=True)
    response_class = models.CharField(max_length=250, null=True, blank=True)
    content_type = models.CharField(max_length=250, null=True, blank=True)
    
    # Single Object Mixin
    model = models.ForeignKey('TrackedModel',on_delete=models.CASCADE, null=True, blank=True)
    queryset = models.CharField(max_length=250, null=True, blank=True)
    slug_field = models.ForeignKey('TrackedField', related_name='view_slug_field', on_delete=models.CASCADE,null=True, blank=True)
    slug_url_kwarg = models.CharField(max_length=250, null=True, blank=True)
    pk_url_kwarg = models.CharField(max_length=250, null=True, blank=True)
    context_object_name = models.CharField(max_length=250, null=True, blank=True)
    query_pk_and_slug = models.CharField(max_length=250, null=True, blank=True)

    # Single Object Template Response Mixin
    template_name_field = models.ForeignKey('TrackedField', related_name='view_template_name_field', on_delete=models.CASCADE, null=True, blank=True)
    template_name_suffix = models.CharField(max_length=250, null=True, blank=True)

    # Multiple Object Mixin
    allow_empty = models.BooleanField(null=True, blank=True)
    ordering = models.CharField(max_length=250, null=True, blank=True)
    paginate_by = models.SmallIntegerField(null=True, blank=True)
    paginate_orphans = models.SmallIntegerField(null=True, blank=True)
    page_kwarg = models.CharField(max_length=250, null=True, blank=True)
    paginator_class = models.CharField(max_length=250, null=True, blank=True)
    context_object_name = models.CharField(max_length=250, null=True, blank=True)
    
    # Form Mixin
    initial = models.TextField(null=True, blank=True)
    form_class = models.CharField(max_length=250, null=True, blank=True)
    prefix = models.CharField(max_length=250, null=True, blank=True)

    # Model Form
    fields = models.ManyToManyField(TrackedField, related_name='view_model_form_fields')

    # Year/Month/Day/Week Mixin
    year_format = models.CharField(max_length=250, null=True, blank=True)
    year = models.CharField(max_length=250, null=True, blank=True)
    month_format = models.CharField(max_length=250, null=True, blank=True)
    month = models.CharField(max_length=250, null=True, blank=True)
    day_format = models.CharField(max_length=250, null=True, blank=True)
    day = models.CharField(max_length=250, null=True, blank=True)
    week_format = models.CharField(max_length=250, null=True, blank=True)
    week = models.CharField(max_length=250, null=True, blank=True)

    # Date Mixin
    date_field = models.ForeignKey('TrackedField', related_name='view_date_field', on_delete=models.CASCADE, null=True, blank=True)
    allow_future = models.BooleanField(null=True, blank=True)
    
    # BaseDateListView
    allow_empty = models.BooleanField(null=True, blank=True)


class Mixin(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey('TrackedApp', on_delete=models.CASCADE)
    base_class = models.CharField(
        max_length=2,
        choices=DefaultMixins.choices,
    )
    methods = models.ManyToManyField(Method)
    # Context Mixin
    extra_context = models.TextField(null=True, blank=True)
    
    # Template Response mixin
    template_name = models.CharField(max_length=250, null=True, blank=True)
    template_engine = models.CharField(max_length=250, null=True, blank=True)
    response_class = models.CharField(max_length=250, null=True, blank=True)
    content_type = models.CharField(max_length=250, null=True, blank=True)
    
    # Single Object Mixin
    model = models.ForeignKey('TrackedModel',on_delete=models.CASCADE, null=True, blank=True)
    queryset = models.CharField(max_length=250, null=True, blank=True)
    slug_field = models.ForeignKey('TrackedField', related_name='mixin_slug_field', on_delete=models.CASCADE,null=True, blank=True)
    slug_url_kwarg = models.CharField(max_length=250, null=True, blank=True)
    pk_url_kwarg = models.CharField(max_length=250, null=True, blank=True)
    context_object_name = models.CharField(max_length=250, null=True, blank=True)
    query_pk_and_slug = models.CharField(max_length=250, null=True, blank=True)

    # Single Object Template Response Mixin
    template_name_field = models.ForeignKey('TrackedField', related_name='mixin_template_name_field', on_delete=models.CASCADE, null=True, blank=True)
    template_name_suffix = models.CharField(max_length=250, null=True, blank=True)

    # Multiple Object Mixin
    allow_empty = models.BooleanField(null=True, blank=True)
    ordering = models.CharField(max_length=250, null=True, blank=True)
    paginate_by = models.SmallIntegerField(null=True, blank=True)
    paginate_orphans = models.SmallIntegerField(null=True, blank=True)
    page_kwarg = models.CharField(max_length=250, null=True, blank=True)
    paginator_class = models.CharField(max_length=250, null=True, blank=True)
    context_object_name = models.CharField(max_length=250, null=True, blank=True)
    
    # Form Mixin
    initial = models.TextField(null=True, blank=True)
    form_class = models.CharField(max_length=250, null=True, blank=True)
    prefix = models.CharField(max_length=250, null=True, blank=True)

    # Model Form
    fields = models.ManyToManyField(TrackedField, related_name='mixin_model_form_fields')

    # Year/Month/Day/Week Mixin
    year_format = models.CharField(max_length=250, null=True, blank=True)
    year = models.CharField(max_length=250, null=True, blank=True)
    month_format = models.CharField(max_length=250, null=True, blank=True)
    month = models.CharField(max_length=250, null=True, blank=True)
    day_format = models.CharField(max_length=250, null=True, blank=True)
    day = models.CharField(max_length=250, null=True, blank=True)
    week_format = models.CharField(max_length=250, null=True, blank=True)
    week = models.CharField(max_length=250, null=True, blank=True)

    # Date Mixin
    date_field = models.ForeignKey('TrackedField', related_name='mixin_date_field', on_delete=models.CASCADE, null=True, blank=True)
    allow_future = models.BooleanField(null=True, blank=True)
    
    # BaseDateListView
    allow_empty = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name

