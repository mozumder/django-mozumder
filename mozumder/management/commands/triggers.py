import sqlparse
import pprint

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.apps import AppConfig
from django.db import models
from django.db import connection
from ...db.materializedviews.materializedviews import MaterializedViewModel
from ...db.materializedviews.fields import MaterializedForeignKey

pp = pprint.PrettyPrinter(indent=4)

class Command(BaseCommand):

    help = 'Manage database materialized view triggers.'
    
    def add_arguments(self, parser):
        
        parser.add_argument(
            '-e','--enable',
            action='store_true',
            dest='enable_triggers',
            default=False,
            help='Enable Materialized View Triggers',
            )

        parser.add_argument(
            '-d','--disable',
            action='store_true',
            dest='disable_triggers',
            default=False,
            help='Disable Materialized View Triggers',
            )

        parser.add_argument(
            '-s','--show_sql',
            action='store_true',
            dest='show_sql',
            default=False,
            help='Show triggers SQL (both to enable and disable)',
            )

        parser.add_argument(
            '-c','--count',
            action='store',
            dest='count',
            type=int,
            default=1,
            help='Number of sets',
            ),

        parser.add_argument(
            'modelname',
            action='store',
            nargs='*',
            default=None,
            help='Specific models you want triggered (or all models if none selected)',
            )

    def handle(self, *args, **options):
    
        all_models = []
        mat_view_models = []
        insert_models = {}
        update_models = {}
        delete_models = {}
        for model in apps.get_models():
            all_models.append(model)
            if issubclass(model, MaterializedViewModel):
                mat_view_models.append(model)
        for model in mat_view_models:
            try:
                secondary_foreign_key = model.secondary_foreign_key
            except:
                secondary_foreign_key = model.primary_foreign_key
            
            secondary_field = model._meta.get_field(secondary_foreign_key)
                
            field = model._meta.get_field(secondary_foreign_key)

            try:
                modelslist = insert_models[field.related_model]
            except:
                modelslist = []
            modelslist.append(model)
            insert_models[field.related_model] = modelslist

            for field in model._meta.get_fields():
                if isinstance(field, MaterializedForeignKey):
                    try:
                        modelslist = update_models[field.related_model]
                    except:
                        modelslist = []
                    if model not in modelslist:
                        modelslist.append(model)
                    update_models[field.related_model] = modelslist

                    if field.remote_field.on_delete == models.SET_NULL:
                        try:
                            modelslist = delete_models[field.related_model]
                        except:
                            modelslist = []
                        if model not in modelslist:
                            modelslist.append(model)
                        delete_models[field.related_model] = modelslist
        
        insert_triggers = {}
        update_triggers = {}
        delete_triggers = {}

        enable_sql = []
        disable_sql = []



        for source_model in insert_models:
            insert = False
            insert_sql = [f"""CREATE OR REPLACE FUNCTION
 {source_model._meta.db_table}_insert()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
 """]
            for target_model in insert_models[source_model]:
                try:
                    secondary_foreign_key = \
                        target_model.secondary_foreign_key
                except:
                    secondary_foreign_key = \
                        target_model.primary_foreign_key
                
                secondary_foreign_key += \
                    target_model.objects.material_view_field_id
                
                insert_statement = \
                    target_model.objects._create_insert_sql(
                        target_model._meta.db_table,
                        target_model.objects.get_view_name
                    )
                if insert_statement:
                    insert = True
                insert_sql.append(insert_statement)
                insert_sql.append(
                    f'\n WHERE\n  {secondary_foreign_key}=new.id\n ;\n'
                )
#               print("------- get_view= ------")
#               print(sqlparse.format(target_model.objects.get_view, reindent=True,
#                        keyword_case='upper'))
            insert_sql.append(f""" RETURN NEW;
 END;
$$;

CREATE TRIGGER
 {source_model._meta.db_table}_insert
AFTER INSERT ON
 "{source_model._meta.db_table}"
FOR EACH ROW EXECUTE FUNCTION
 {source_model._meta.db_table}_insert()
;
""")
#           print('---- Insert trigger ----')
#           print("".join(insert_sql))
            if insert == True:
                enable_sql.append("".join(insert_sql))
                disable_sql.append(
                    f'DROP TRIGGER IF EXISTS '
                    f'{source_model._meta.db_table}_insert '
                    f'ON "{source_model._meta.db_table}";\n'
                    f'DROP FUNCTION IF EXISTS '
                    f'{source_model._meta.db_table}_insert();\n'
                )

        for source_model in update_models:
            update = False
            update_sql = [f"""CREATE OR REPLACE FUNCTION
 {source_model._meta.db_table}_update(_old INTEGER,_new INTEGER)
RETURNS VOID
SECURITY DEFINER
LANGUAGE SQL
AS $$
"""]
            for target_model in update_models[source_model]:
                remotes = []
                dirty_bit = False
                
                for field in target_model._meta.get_fields():
                    if isinstance(field, MaterializedForeignKey):
                        if field.related_model == source_model:
#                           print("found related_model", field)
                            field_name = field.get_attname_column()[1]
                            ref = (
                                f' "{target_model._meta.db_table}".'
                                f'"{field_name}" '
                                f'in(_old, _new)\n'
                            )
                            remotes.append(ref)

                    if hasattr(field,'dirty_bit'):
                        if field.dirty_bit==True:
                            dirty_bit = True
                        
                related = "  OR".join(remotes)
                if dirty_bit==True:
                    update_statement = (f' UPDATE\n '
                    f' {target_model._meta.db_table}\n SET\n'
                    f'  {field.name} = TRUE\n WHERE\n {related}'
                    f' ;\n')
                    update_sql.append(update_statement)
                    update = True

            update_sql.append(f"""$$;

CREATE OR REPLACE FUNCTION
 {source_model._meta.db_table}_update()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
  PERFORM {source_model._meta.db_table}_update(old.id, new.id);
  RETURN NEW;
 END;
$$;

CREATE TRIGGER
 {source_model._meta.db_table}_update
AFTER UPDATE ON
 "{source_model._meta.db_table}"
FOR EACH ROW EXECUTE FUNCTION
 {source_model._meta.db_table}_update()
;
""")
#           print('---- Update trigger ----')
#           print("".join(update_sql))
            if update == True:
                enable_sql.append("".join(update_sql))
                disable_sql.append(
                    f'DROP TRIGGER IF EXISTS '
                    f'{source_model._meta.db_table}_update '
                    f'ON "{source_model._meta.db_table}";\n'
                    f'DROP FUNCTION IF EXISTS '
                    f'{source_model._meta.db_table}_update();\n'
                    f'DROP FUNCTION IF EXISTS '
                    f'{source_model._meta.db_table}_update(INTEGER,INTEGER);\n'
                )

        for source_model in delete_models:
            delete = False
            delete_sql = [f"""CREATE OR REPLACE FUNCTION
 {source_model._meta.db_table}_delete(_old INTEGER)
RETURNS VOID
SECURITY DEFINER
LANGUAGE SQL
AS $$
"""]
            for target_model in delete_models[source_model]:
                remotes = []
                dirty_bit = False
                
                for field in target_model._meta.get_fields():
                    if isinstance(field, MaterializedForeignKey):
                        if field.related_model == source_model and \
                            field.remote_field.on_delete == \
                            models.SET_NULL:
                            field_name = field.get_attname_column()[1]
                            ref = (
                                f' "{target_model._meta.db_table}".'
                                f'"{field_name}" = _old\n'
                            )
                            remotes.append(ref)

                    if hasattr(field,'dirty_bit'):
                        if field.dirty_bit==True:
                            dirty_bit = True
                        
                related = "  OR".join(remotes)
                if dirty_bit==True:
                    delete_statement = (f' UPDATE\n '
                    f' {target_model._meta.db_table}\n SET\n'
                    f'  {field.name} = TRUE\n WHERE\n {related}'
                    f' ;\n')
                    delete_sql.append(delete_statement)
                    delete = True

            delete_sql.append(f"""$$;

CREATE OR REPLACE FUNCTION
 {source_model._meta.db_table}_delete()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
  PERFORM {source_model._meta.db_table}_delete(old.id);
  RETURN OLD;
 END;
$$;

CREATE TRIGGER
 {source_model._meta.db_table}_delete
AFTER DELETE ON
 "{source_model._meta.db_table}"
FOR EACH ROW EXECUTE FUNCTION
 {source_model._meta.db_table}_delete()
;
""")

            if delete == True:
                enable_sql.append("".join(delete_sql))
                disable_sql.append(
                    f'DROP TRIGGER IF EXISTS '
                    f'{source_model._meta.db_table}_delete '
                    f'ON "{source_model._meta.db_table}";\n'
                    f'DROP FUNCTION IF EXISTS '
                    f'{source_model._meta.db_table}_delete();\n'
                    f'DROP FUNCTION IF EXISTS '
                    f'{source_model._meta.db_table}_delete(integer);\n'
                )

        if options['show_sql']:
            print("".join(enable_sql))
            print("".join(disable_sql))

        if options['enable_triggers']:
            print("Enabling materialized views database triggers")
            sql = "".join(enable_sql)
            cursor = connection.cursor()
            cursor.execute(sql)
            cursor.close()

        if options['disable_triggers']:
            print("Disabling materialized views database triggers")
            sql = "".join(disable_sql)
            cursor = connection.cursor()
            cursor.execute(sql)
            cursor.close()
