import os

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder
from ...models.development import *
from ... import FieldTypes, OnDelete, ViewBaseClass
from ..utilities.modelwriter import *
from ..utilities.name_case import *

class Command(BaseCommand):

    help = """Add a new model to an app. Models takes a list of field arguments. Each field argument is divided up as:

    name:type:options:[unamed properties[:...][:named properties[:...]]]

Options are set from a list of single character switches for each field:

    p: Field is model's primary key
    r: Has a detail view
    e: Editable field
    l: Is shown in list view
    L: Is shown in list view with a hyperlink to detail view
    _: Allow null values in database
    -: Allow null values in database and forms
    i: Create a database index for the field
    U: Field is Unique
    D: Field is Unique for Date
    M: Field is Unique for Month
    Y: Field is Unique for Year
    a: Auto now
    A: Auto now add

Depending on field type, there may be required properties or [optional] unnamed properties:

    BooleanField::[default_bool]
    CharField::max_length:[default_text]
    BinaryField::max_length
    TextField::[max_length]
    SmallIntegerField::[default_smallint]
    BigIntegerField::[default_bigint]
    DateTimeField::[default_datetime]
    ForeignKey::to:on_delete:[related_name]
    ForeignKey::to:[related_name]
"""
    
    def add_arguments(self, parser):

        parser.add_argument(
            '--abstract',
            action='store_true',
            default=None,
            help="Abstract model",
            )
        parser.add_argument(
            '--app_label',
            action='store',
            default=None,
            help="If a model is defined outside of an application in INSTALLED_APPS, it must declare which app it belongs to. If you want to represent a model with the format app_label.object_name or app_label.model_name you can use model._meta.label or model._meta.label_lower respectively.",
            )
        parser.add_argument(
            '--base_manager_name',
            action='store',
            default=None,
            help="The attribute name of the manager, for example, 'objects', to use for the model’s _base_manager.",
            )
        parser.add_argument(
            '--db_table',
            action='store',
            default=None,
            help="The name of the database table to use for the model",
            )
        parser.add_argument(
            '--db_tablespace',
            action='store',
            default=None,
            help="The name of the database tablespace to use for this model. The default is the project’s DEFAULT_TABLESPACE setting, if set. If the backend doesn’t support tablespaces, this option is ignored.",
            )
        parser.add_argument(
            '--default_manager_name',
            action='store',
            default=None,
            help="The name of the manager to use for the model’s _default_manager.",
            )
        parser.add_argument(
            '--default_related_name',
            action='store',
            default=None,
            help="""The name that will be used by default for the relation from a related object back to this one. The default is <model_name>_set.

This option also sets related_query_name.

As the reverse name for a field should be unique, be careful if you intend to subclass your model. To work around name collisions, part of the name should contain '%(app_label)s' and '%(model_name)s', which are replaced respectively by the name of the application the model is in, and the name of the model, both lowercased. See the paragraph on related names for abstract models.""",
            )
        parser.add_argument(
            '--get_latest_by',
            action='store',
            default=None,
            help="Model's Meta 'get_latest_by' fields, seperated by colons. Underscore in front of field name indicates descending. Underscore after field name indicates nulls last. The name of a field or a list of field names in the model, typically DateField, DateTimeField, or IntegerField. This specifies the default field(s) to use in your model Manager’s latest() and earliest() methods.",
            )
        parser.add_argument(
            '--managed',
            action='store_true',
            default=None,
            help="""Defaults to True, meaning Django will create the appropriate database tables in migrate or as part of migrations and remove them as part of a flush management command. That is, Django manages the database tables’ lifecycles.

If False, no database table creation, modification, or deletion operations will be performed for this model. This is useful if the model represents an existing table or a database view that has been created by some other means. This is the only difference when managed=False. All other aspects of model handling are exactly the same as normal. This includes

Adding an automatic primary key field to the model if you don’t declare it. To avoid confusion for later code readers, it’s recommended to specify all the columns from the database table you are modeling when using unmanaged models.

If a model with managed=False contains a ManyToManyField that points to another unmanaged model, then the intermediate table for the many-to-many join will also not be created. However, the intermediary table between one managed and one unmanaged model will be created.

If you need to change this default behavior, create the intermediary table as an explicit model (with managed set as needed) and use the ManyToManyField.through attribute to make the relation use your custom model.

For tests involving models with managed=False, it’s up to you to ensure the correct tables are created as part of the test setup.

If you’re interested in changing the Python-level behavior of a model class, you could use managed=False and create a copy of an existing model. However, there’s a better approach for that situation: Proxy models.""",
            )
        parser.add_argument(
            '--order_with_respect_to',
            action='store',
            default=None,
            help="Makes this object orderable with respect to the given field, usually a ForeignKey. This can be used to make related objects orderable with respect to a parent object. When order_with_respect_to is set, two additional methods are provided to retrieve and to set the order of the related objects: get_RELATED_order() and set_RELATED_order(), where RELATED is the lowercased model name. The related objects also get two methods, get_next_in_order() and get_previous_in_order(), which can be used to access those objects in their proper order. ",
            )
        parser.add_argument(
            '--ordering',
            action='store',
            default=None,
            help="Model's Meta 'ordering' fields, seperated by colons. Underscore in front of field name indicates descending. Underscore after field name indicates nulls last. The default ordering for the object, for use when obtaining lists of objects.",
            )
        parser.add_argument(
            '--permissions',
            action='store',
            default=None,
            help="Model's Meta 'permissions' fields, with tuples separted by colons. Each tuple is separated by a forward slash.",
            )
        parser.add_argument(
            '--default_permissions',
            action='store',
            default=None,
            help="Model's Meta 'default_permissions' fields, with permissions seperated by colons. Defaults to ('add', 'change', 'delete', 'view'). You may customize this list, for example, by setting this to an empty list if your app doesn’t require any of the default permissions. It must be specified on the model before the model is created by migrate in order to prevent any omitted permissions from being created.",
            )
        parser.add_argument(
            '--proxy',
            action='store_true',
            default=None,
            help="If proxy = True, a model which subclasses another model will be treated as a proxy model.",
            )
        parser.add_argument(
            '--select_on_save',
            action='store_true',
            default=None,
            help="Determines if Django will use the pre-1.6 django.db.models.Model.save() algorithm. The old algorithm uses SELECT to determine if there is an existing row to be updated. The new algorithm tries an UPDATE directly. In some rare cases the UPDATE of an existing row isn’t visible to Django. An example is the PostgreSQL ON UPDATE trigger which returns NULL. In such cases the new algorithm will end up doing an INSERT even when a row exists in the database. Usually there is no need to set this attribute. The default is False.",
            )
        parser.add_argument(
            '--indexes',
            action='store',
            default=None,
            help="Model's Meta 'indexes' fields, with tuples seperated by colons, with the first element of each tuple being the index name. Each tuple is separated by a forward slash.",
            )

        parser.add_argument(
            '--verbose_name',
            action='store',
            help="Model's verbose name",
            )
        parser.add_argument(
            '--verbose_name_plural',
            action='store',
            help="Model's plural verbose name",
            )
        parser.add_argument(
            'app_name',
            action='store',
            help='App name',
            )
        parser.add_argument(
            'model_name',
            action='store',
            help='Model name',
            )
        parser.add_argument(
            'field',
            action='store',
            nargs='+',
            help="Model fields in format: name:type:[args:...] For foreignkeys, the format is: name:type:relation:on_delete:[args:...]",
            )
            
    def handle(self, *args, **options):

        project_name = settings.PROJECT_NAME
        app_name = options['app_name']
        model_name = options['model_name']
        model_code_name = CamelCase_to_snake_case(model_name)
        fields_list = options['field']
        
        # Create app
        tracked_app, app_created = TrackedApp.objects.get_or_create(name=app_name)
        tracked_app.save()

        # Create model
        tracked_model, model_created = TrackedModel.objects.get_or_create(owner=tracked_app, name=model_name)

        # Build models lists
        show_in_detail_view = False
        editable = True
        show_in_list_view = False
        link_in_list_view = False
        db_tablespace = None
        db_column = None
        db_index = False
        blank = False
        null = False
        error_messages = {}
        validators = []
        help_text = None
        primary_key = False
        unique = False
        unique_for_date = False
        unique_for_month = False
        unique_for_year = False
        auto_now = False
        auto_now_add = False

        auto_created = False
        serialize = True

        has_primary_key = False

        for field in fields_list:
            field_name, field_type, field_properties, *field_params = field.split(":")

            field, field_created = TrackedField.objects.get_or_create(name=field_name, owner=tracked_model)
            
            field.verbose_name = snake_case_to_verbose(field_name)

            # Get field properties
            if 'k' in field_properties:
                field.primary_key = True
                has_primary_key = True
            if '_' in field_properties:
                field.null = True
            if '-' in field_properties:
                field.blank = True
                field.null = True
            if 'r' in field_properties:
                field.show_in_detail_view = True
            if 'e' in field_properties:
                field.editable = True
            if 'l' in field_properties:
                field.show_in_list_view = True
            if 'L' in field_properties:
                field.show_in_list_view = True
                field.link_in_list_view = True
            if 'i' in field_properties:
                field.db_index = True
            if 'U' in field_properties:
                field.unique = True
            if 'D' in field_properties:
                field.unique_for_date = True
            if 'M' in field_properties:
                field.unique_for_month = True
            if 'Y' in field_properties:
                field.unique_for_year = True
            if 'a' in field_properties:
                field.auto_now = True
            if 'A' in field_properties:
                field.auto_now_add = True
            
            if field_type == 'BooleanField':
                if len(field_params) > 0:
                    field.default_bool = field_params[0]
            elif field_type == 'CharField':
                field.max_length = int(field_params[0]) if field_params[0] else None
                if len(field_params) > 1:
                    field.default_text = field_params[1] if field_params[1] else None
            elif field_type == 'BinaryField':
                field.max_length = int(field_params[0]) if field_params[0] else None
            elif field_type == 'TextField':
                if len(field_params) > 0:
                    field.default_text = field_params[0] if field_params[1] else None
            elif field_type == 'SmallIntegerField':
                if len(field_params) > 0:
                    field.default_smallint = int(field_params[0]) if field_params[0] else None
            elif field_type == 'BigIntegerField':
                if len(field_params) > 0:
                    field.default_bigint = int(field_params[0]) if field_params[0] else None
            elif field_type == 'DateTimeField':
                if len(field_params) > 0:
                    field.default_datetime = field_params[0]
            elif field_type == 'ForeignKey':
                field.to = field_params[0]
                field.on_delete = OnDelete[field_params[1]]
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        field.related_name = param.split('=')[1]
                    i += 1
            elif field_type == 'ManyToManyField':
                field.to = field_params[0]
                i = 0
                for param in field_params:
                    if param.startswith('related_name='):
                        field.related_name = param.split('=')[1]
                    i += 1
            elif field_type == 'ImageField' or field_type == 'FileField':
                i = 0
                for param in field_params:
                    if param.startswith('upload_to='):
                        field.upload_to = param.split('=')[1]
                    i += 1
            field.type=FieldTypes[field_type.upper()]
            field.save()

        if has_primary_key == False:
            field, field_created = TrackedField.objects.get_or_create(
                name='id', owner=tracked_model)
            field.type=FieldTypes['AUTOFIELD']
            field.auto_created = True
            field.primary_key = True
            field.serialize = False
            field.verbose_name = 'ID'
            field.save()
            
        # Model meta options
        if options['abstract']:
            tracked_model.abstract = True
        if options['app_label']:
            tracked_model.app_label = options['app_label']
        if options['base_manager_name']:
            tracked_model.base_manager_name = options['base_manager_name']
        if options['db_table']:
            tracked_model.db_table = options['db_table']
        if options['db_tablespace']:
            tracked_model.db_tablespace = options['db_tablespace']
        if options['default_manager_name']:
            tracked_model.default_manager_name = options['default_manager_name']
        if options['default_related_name']:
            tracked_model.default_related_name = options['default_related_name']
        if options['get_latest_by']:
            get_latest_bys = options['get_latest_by'].split(':')
            number = 0
            for field_name in get_latest_bys:
                descending = False
                nulls_last = False
                if field_name[0] == '_':
                    descending = True
                    field_name = field_name[1:]
                if field_name[-1] == '_':
                    nulls_last = True
                    field_name = field_name[:-1]
                field = TrackedField.objects.get(name=field_name, owner=tracked_model)
                get_latest_by = Latest.objects.create(latest_field=field, latest_model=tracked_model, number=number, descending=descending, nulls_last=nulls_last)
                get_latest_by.save()
                number+=1
        if options['managed']:
            tracked_model.managed = options['managed']
        if options['order_with_respect_to']:
            tracked_model.order_with_respect_to = options['order_with_respect_to']
        if options['ordering']:
            orders = options['ordering'].split(':')
            number = 0
            for field_name in orders:
                descending = False
                nulls_last = False
                if field_name[0] == '_':
                    descending = True
                    field_name = field_name[1:]
                if field_name[-1] == '_':
                    nulls_last = True
                    field_name = field_name[:-1]
                field = TrackedField.objects.get(name=field_name, owner=tracked_model)
                order = Ordering.objects.create(target_field=field, source=tracked_model, number=number, descending=descending, nulls_last=nulls_last)
                order.save()
                number+=1
        if options['permissions']:
            permissions = options['permissions'].split('/')
            number = 0
            for pair in permissions:
                permission_code, human_readable_permission_name = pair.split(':')
                extra_permission = ExtraPermission.objects.create(permission_code=f"'{permission_code}'", human_readable_permission_name=f"'{human_readable_permission_name}'")
                extra_permission.save()
                tracked_model.permissions.add(extra_permission)
                number+=1

        if options['default_permissions']:
            default_permissions = options['default_permissions'].split(':')
        else:
            default_permissions = ('add', 'change', 'delete', 'view')
        for permission_code in default_permissions:
            default_permission, created = DefaultPermission.objects.get_or_create(permission_code=permission_code)
            tracked_model.default_permissions.add(default_permission)
        if options['proxy']:
            tracked_model.proxy = options['proxy']
        if options['select_on_save']:
            tracked_model.select_on_save = options['select_on_save']

        if options['indexes']:
            indexes = options['indexes'].split('/')
            for index in indexes:
                index_name, *index_fields = index.split(':')
                # Create a new index object, even if name isn't unique
                index_obj = Index.objects.create(name=index_name, owner=tracked_model)
                index_obj.save()
                for field_name in index_fields:
                    field = TrackedField.objects.get(name=field_name, owner=tracked_model)
                    index_obj.fields.add(field)
                tracked_model.indexes.add(index_obj)

        if options['verbose_name']:
            tracked_model.verbose_name = options['verbose_name']
        if options['verbose_name_plural']:
            tracked_model.verbose_name_plural = options['verbose_name_plural']
        tracked_model.save()

# The following are the operations that are built by default for
# every model:
#
# Read One Item
# Read All
# Read Filter/Exclude
# Read Stubs List
# Search Items
# Sort Items
# Reorder Items
# Add One Item
# Insert One Item
# Add Multiple Items
# Duplicate Item
# Update Item
# Update All
# Update Filter/Exclude
# Validate Item
# Delete Item
# Delete All
# Delete Filter/Exclude
# Search Through Field
# Add Item to Field
# Add Multiple Items to Field
# Increment Field
# Decrement Field
# Validate Field
# Duplicate Items to Field
# Delete Item from Field
# Delete All Items from Field
# Delete Multiple Items from Field
# Operation on View
#
# Enable operations you need by uncommenting out the operation in
# the urls.py file

        # Build default views for this model
        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}DetailView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['DETAILVIEW']
        view.model = tracked_model
        view.url = f"'{model_name}/<int:pk>'"
        view.url_name = f"'{model_code_name}_detail'"
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}ListView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['LISTVIEW']
        view.model = tracked_model
        view.url = f"'{model_name}/'"
        view.url_name = f"'{model_code_name}_list'"
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}CreateView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['CREATEVIEW']
        view.model = tracked_model
        view.template_name_suffix = "'_create_form'"
        view.url = f"'{model_name}/create'"
        view.url_name = f"'{model_code_name}_create'"
        view.save()
        view.fields.add(*TrackedField.objects.filter(owner=tracked_model))

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}CopyView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['CREATEVIEW']
        view.model = tracked_model
        view.template_name_suffix = "'_copy_form'"
        view.url = f"'{model_name}/copy'"
        view.url_name = f"'{model_code_name}_copy'"
        view.save()
        view.fields.add(*TrackedField.objects.filter(owner=tracked_model))

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}UpdateView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['UPDATEVIEW']
        view.model = tracked_model
        view.template_name_suffix = "'_create_form'"
        view.url = f"'{model_name}/<int:pk>/update'"
        view.url_name = f"'{model_code_name}_update'"
        view.save()
        view.fields.add(*TrackedField.objects.filter(owner=tracked_model))

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}DeleteView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['DELETEVIEW']
        view.model = tracked_model
        view.template_name_suffix = "'_create_form'"
        view.success_url = f"reverse_lazy('{model_code_name}_list')"
        view.url = f"'{model_name}/<int:pk>/delete'"
        view.url_name = f"'{model_code_name}_delete'"
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'search_{model_code_name}', owner=tracked_app)
        view.class_based_view = False
        view.model = tracked_model
        view.url = f"'{model_name}/search'"
        view.url_name = f"'json_search_{model_code_name}'"
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}JSONDetailView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['DETAILVIEW']
        view.model = tracked_model
        view.url = f"'detail/{model_name}/<int:pk>'"
        view.url_name = f"'json_{model_code_name}_detail'"
        view.api_url = True
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'{model_name}JSONListView', owner=tracked_app)
        view.class_based_view = True
        view.base_class = ViewBaseClass['LISTVIEW']
        view.model = tracked_model
        view.url = f"'list/{model_name}'"
        view.url_name = f"'json_{model_code_name}_list'"
        view.api_url = True
        view.save()

        view, view_created = TrackedView.objects.get_or_create(
                name=f'json_search_{model_code_name}', owner=tracked_app)
        view.class_based_view = False
        view.model = tracked_model
        view.url = f"'search/{model_name}'"
        view.url_name = f"'search_{model_code_name}'"
        view.api_url = True
        view.save()

