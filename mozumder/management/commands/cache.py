from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.apps import apps
from django.db import connection

from ...db.materializedviews.materializedviews import MaterializedViewModel


class Command(BaseCommand):

    help = 'Manage Redis cache.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            '-c','--clear',
            action='store_true',
            dest='cache_clear',
            default=False,
            help='Clear Entire Redis Cache',
            )
        parser.add_argument(
            '-e','--enable_triggers',
            action='store_true',
            dest='cache_enable_triggers',
            default=False,
            help='Enable Postgre triggers on Materialized Views',
            )
        parser.add_argument(
            '-d','--disable_triggers',
            action='store_true',
            dest='cache_disable_triggers',
            default=False,
            help='Disable Postgre triggers on Materialized Views',
            )
        parser.add_argument(
            '-l','--listen',
            action='store_true',
            dest='db_listen',
            default=False,
            help='Listen to Database for Cache Invalidation Events',
            )
        parser.add_argument(
            '-s','--show_sql',
            action='store_true',
            dest='show_sql',
            default=False,
            help='Show SQL for cache triggers',
            )

    def handle(self, *args, **options):

        prepared_statements = 'include/sql/triggers/globals/prepare.sql'
        
        if options['cache_clear']:
            cache.clear()

        if options['db_listen']:
            from ..utilities.invalidator import CacheInvalidator
            CacheInvalidator.listen()
            return

        all_models = []
        mat_view_models = []
        insert_models = {}
        update_models = {}
        delete_models = {}
        for model in apps.get_models():
            all_models.append(model)
            if issubclass(model, MaterializedViewModel):
                mat_view_models.append(model)
                

        enable_sql = """
create or replace function cache_notify(_msg varchar)
returns void
security definer
language sql
as $$
select pg_notify('cache', _msg);
$$;
"""
        for model in mat_view_models:
            new_key = f"'{model.primary_foreign_key}:' || new.{model.primary_foreign_key}"
            old_key = f"'{model.primary_foreign_key}:' || old.{model.primary_foreign_key}"
            if hasattr(model,"additional_view_key"):
                new_key = f"{new_key} || ':{model.additional_view_key}:' || new.{model.additional_view_key}"
                old_key = f"{old_key} || ':{model.additional_view_key}:' || old.{model.additional_view_key}"

            enable_sql = enable_sql + f"""
CREATE OR REPLACE FUNCTION
 {model._meta.db_table}_insert()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
  PERFORM cache_notify('{model.__name__}:' || {new_key});
  RETURN NEW;
 END;
$$;

CREATE TRIGGER
  {model._meta.db_table}_insert
AFTER INSERT ON
  "{model._meta.db_table}"
FOR EACH ROW EXECUTE PROCEDURE
  {model._meta.db_table}_insert();

CREATE OR REPLACE FUNCTION
 {model._meta.db_table}_update()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
  IF old.id = new.id THEN
   PERFORM cache_notify('{model.__name__}:' || {new_key});
  ELSE
   PERFORM cache_notify('{model.__name__}:' || {old_key});
   PERFORM cache_notify('{model.__name__}:' || {new_key});
  END IF;
  RETURN NEW;
 END;
$$;

CREATE TRIGGER
  {model._meta.db_table}_update
AFTER UPDATE ON
  "{model._meta.db_table}"
FOR EACH ROW EXECUTE PROCEDURE
  {model._meta.db_table}_update();

CREATE OR REPLACE FUNCTION
 {model._meta.db_table}_delete()
RETURNS TRIGGER
SECURITY DEFINER
LANGUAGE PLPGSQL
AS $$
 BEGIN
  PERFORM cache_notify('{model.__name__}:' || {old_key});
  RETURN OLD;
 END;
$$;

CREATE TRIGGER
  {model._meta.db_table}_delete
AFTER DELETE ON
  "{model._meta.db_table}"
FOR EACH ROW EXECUTE PROCEDURE
  {model._meta.db_table}_delete();

"""

        disable_sql = ''
        for model in mat_view_models:

            disable_sql = disable_sql + f"""
drop function if exists cache_notify(varchar);

DROP TRIGGER IF EXISTS
 {model._meta.db_table}_insert
ON
 "{model._meta.db_table}";
DROP FUNCTION IF EXISTS {model._meta.db_table}_insert();
DROP TRIGGER IF EXISTS
 {model._meta.db_table}_update
ON
 "{model._meta.db_table}";
DROP FUNCTION IF EXISTS {model._meta.db_table}_update();
DROP TRIGGER IF EXISTS
 {model._meta.db_table}_delete
ON
 "{model._meta.db_table}";
DROP FUNCTION IF EXISTS {model._meta.db_table}_delete();
"""

        if options['cache_enable_triggers']:
            print('Turning on cache Postgresql triggers')
            cursor = connection.cursor()
            cursor.execute(enable_sql)
            cursor.close()
        if options['cache_disable_triggers']:
            print('Turning off cache Postgresql triggers')
            cursor = connection.cursor()
            cursor.execute(disable_sql)
            cursor.close()

        if options['show_sql']:
            print(enable_sql)
