import sys
import traceback
from functools import reduce
from datetime import datetime
import sqlparse
import pprint
from django.db import models
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Q, F, ExpressionWrapper, Func, Case, When, Value

import logging
from psycopg2.errors import UndefinedColumn, UndefinedTable, UndefinedObject

logger = logging.getLogger("django")
dblogger = logging.getLogger("database")
pp = pprint.PrettyPrinter(indent=4)
CASCADE = models.CASCADE
SET_NULL = models.SET_NULL

foreign_key_id = "_id"

def get_field_name(model_manager,field):
    if field.db_column == None:
        if isinstance(field,models.ForeignKey):
            return f'{field.name}{foreign_key_id}'
        else:
            return f'{field.name}'
    else:
        return f'{field.db_column}'
def get_view_field_name(model_manager,field):
    if isinstance(field,models.ForeignKey):
        return (
            f'{field.name}{foreign_key_id}'
            f'{model_manager.material_view_field_id}')
    else:
        return f'{field.name}{model_manager.material_view_field_id}'

class PreparedStatement():
    def __init__(self,
        model,
        view_name=None,
        get_args=None,
        where_args=None,
        order_by=None,
        limit=None,
        fields=None,
        aliases=None,
        ignore=None,
        extra_view_fields=None,
        active_bit = None,
        start_time = None,
        stop_time = None,
        JSON=False,
        *args, **kwargs
    ):
        self.model = model
        self.get_args = get_args
        cursor = connection.cursor()
        if view_name == None:
            view_name = model.__name__
        if order_by == None:
            if hasattr(model._meta,'ordering'):
                order_by = model._meta.ordering
        self.view_name = view_name
        self.prepare_sql = self.create_prepare_sql(
                view_name,
                model,
                get_args,
                where_args,
                order_by,
                limit,
                fields,
                aliases,
                ignore,
                extra_view_fields,
                active_bit,
                start_time,
                stop_time,
                JSON,
                )
        try:
            cursor.execute(self.prepare_sql)
        except:
            logging.warning(f"Failed to read prepared SQL for {self}")
        cursor.close()
    def create_prepare_sql(
        self,
        view_name=None,
        model=None,
        get_args=None,
        where_args=None,
        order_by=None,
        limit=None,
        fields=None,
        aliases=None,
        ignore=None,
        extra_view_fields=None,
        active_bit = None,
        start_time = None,
        stop_time = None,
        JSON=False,
    ):
        finder = []
        if get_args:
            for arg in get_args:
                finder.append(f'{get_args[arg]}')
            view_args = '(' + ', '.join(finder) + ')'
        else:
            view_args = ''
        self.view_sql, self.view_subquery_sql = self.create_view_statement(
            model, get_args, where_args,
            order_by, limit, fields, aliases, ignore,
            active_bit,start_time,stop_time,
            extra_view_fields,JSON
            )
        return (f'PREPARE\n  {view_name}{view_args}\n'
                f'AS\n{self.view_sql};')
    def create_view_statement(
        self,
        model,
        get_args=None,
        where_args=None,
        order_by=None,
        limit=None,
        fields=None,
        aliases=None,
        ignore=None,
        active_bit = None,
        start_time = None,
        stop_time = None,
        extra_view_fields=None,
        JSON=None,
    ):
        sql = ['SELECT\n']
        if ignore == None:
            ignore = []
        if aliases == None:
            aliases = {}
        if fields == None:
            selected_fields = model._meta.get_fields()
        else:
            selected_fields = [model._meta.get_field(field_name) for field_name in fields]
        select=[]
        for field in selected_fields:
            field_name = get_field_name(self, field)
            if hasattr(field,'source') or hasattr(field,'dirty_bit'):
                if not hasattr(field,'dirty_bit') and field_name not in ignore:
                    try:
                        alias = aliases[field_name]
                    except:
                        alias = field_name
                    select.append(f'  "u"."{field_name}" AS "{alias}"')
            if hasattr(field,'active_bit') and active_bit==None:
                active_bit = field_name
            if hasattr(field,'start_time') and start_time==None:
                start_time = field_name
            if hasattr(field,'stop_time') and stop_time==None:
                stop_time = field_name

        if extra_view_fields:
            for field in extra_view_fields:
                select.append(
                    f'  {extra_view_fields[field]} AS "{field}"')
        sql.append(',\n'.join(select) + f'\nFROM (\n')
        sql.append(
            self._create_lazy_refresh_select(
                model, get_args, where_args,
                order_by, limit, aliases, ignore,
                active_bit,start_time,stop_time
                ))
        sql.append(f') "u"\n')

        finder = None
        if where_args:
            finder = []
            for case in where_args:
                finder.append(f' "u"."{case[0]}" {case[1]} {case[2]}')
        elif get_args or active_bit or start_time or stop_time:
            finder = []
            if get_args:
                count = 1
                for arg in get_args:
                    finder.append(f' "u"."{arg}" = ${count}')
                    count += 1
            if isinstance(active_bit,str):
                finder.append(f' "u"."{active_bit}" = TRUE')
            if isinstance(start_time,str):
                finder.append(f' "u"."{start_time}" <= now()')
            if isinstance(stop_time,str):
                finder.append(f' "u"."{stop_time}" > now()')
        if finder:
            sql.append('WHERE\n' + '\n AND'.join(finder) + '\n')
    
        if order_by:
            ordering_fields = []
            for ordering_field_name in order_by:
                if ordering_field_name[0] == '-':
                    field = model._meta.get_field(ordering_field_name[1:])
                    field_name = get_field_name(self,field)
                    ordering_fields.append(f'"u"."{field_name}" DESC')
                else:
                    field = model._meta.get_field(ordering_field_name)
                    field_name = get_field_name(self,field)
                    ordering_fields.append(f'"u"."{field_name}" ASC')
            sql.append('ORDER BY\n'+ ','.join(ordering_fields) + '\n')
        if limit:
            sql.append(f'LIMIT {limit}')
        sql = ''.join(sql)
        if JSON:
            if limit == 1:
                view_sql = (f'SELECT row_to_json(t)::TEXT\n'
                    f'FROM\n(\n{sql}\n) as t')
                view_subquery_sql = (f'SELECT json_strip_nulls(row_to_json(t))\n'
                    f'FROM\n(\n{sql}\n) as t')
            else:
                view_sql = (f'SELECT json_agg(json_strip_nulls(row_to_json(t)))::TEXT\n'
                    f'FROM\n(\n{sql}\n) as t')
                view_subquery_sql = (f'SELECT json_agg(json_strip_nulls(row_to_json(t)))\n'
                    f'FROM\n(\n{sql}\n) as t')
        else:
            view_sql = sql
            view_subquery_sql = sql

        return view_sql, view_subquery_sql
    def _create_lazy_refresh_select(
        self,
        model,
        get_args=None,
        where_args=None,
        order_by=None,
        limit=None,
        aliases=None,
        ignore=None,
        active_bit = None,
        start_time = None,
        stop_time = None,
    ):
        table_name = model._meta.db_table
        view_name = f'{model.__name__}_lazy_refresh_view'
        sql = [' SELECT\n',]
        fresh_fields = []
        stale_fields = []
        dirty_bit = None

        for field in model._meta.get_fields():
            field_name = get_field_name(self,field)
            if hasattr(field,'source') or hasattr(field,'dirty_bit'):
                if hasattr(field,'dirty_bit'):
                    dirty_bit = field_name
                else:
                    fresh_fields.append(f'  {field_name}')
                    stale_fields.append(f'  t.{field_name}')

        sql.append(',\n'.join(fresh_fields) + f'\n FROM\n  {table_name}\n')

        finder = []
        if where_args == None:
            if get_args:
                count = 1
                for arg in get_args:
                    finder.append(f' {arg} = ${count}')
                    count += 1
        finder.append(f'  {dirty_bit} = FALSE')
        
        id_parameters = [f'"v"."{model.primary_foreign_key}"']
        if hasattr(model,'unique_select_fields'):
            for uniqueid_field in model.unique_select_fields:
                i = model._meta.get_field(uniqueid_field)
                i_name = get_field_name(self,i)
                id_parameters.append(f'"v"."{i_name}"')
        id_parameters_clause = ', '.join(id_parameters)

        
        sql.append(' WHERE\n' + '\n AND'.join(finder) + '\n UNION ALL\n')
        sql.append(' SELECT\n' + ',\n'.join(stale_fields) + '\n')
        sql.append(f' FROM\n  "{table_name}" "v"\n')
        sql.append(f' CROSS JOIN\n  {model.refresh_function_name}'
            f'({id_parameters_clause}) "t"')
        finder = []
        if where_args == None:
            if get_args:
                count = 1
                for arg in get_args:
                    finder.append(f' "v"."{arg}" = ${count}')
                    count += 1
        finder.append(f'  "v"."{dirty_bit}" = TRUE')
        sql.append('\n WHERE \n' + '\n AND'.join(finder))

        return ''.join(sql)
    def disable(self,cursor):
        try:
            cursor.execute(f'DEALLOCATE {self.view_name};')
        except OperationalError as e:
            pass
    def enable(self,cursor):
        cursor.execute(self.prepare_sql)
    def execute(
        self,
        cursor,
        id=None,
    ):
        if id:
            cursor.execute(f'EXECUTE {self.view_name}(%s);', [id])
        else:
            cursor.execute(f'EXECUTE {self.view_name};')
    def fetch(
        self,
        cursor
    ):
        return cursor.fetchone()

class MaterializedViewManager(models.Manager):
    material_view_field_id = "_mview"
    def prepare(self,cursor):
        if hasattr(self.model,'primary_foreign_key'):
            primary_foreign_key = self.model.primary_foreign_key
        else:
            primary_foreign_key = None

        self.get_view, self.get_view_name = self._create_get_view(
            primary_foreign_key)
        self.init_view, self.init_function_name, \
            self.init_function_return_table = self._create_init_view()
        self.refresh_view, self.model.refresh_function_name, \
            self.refresh_function_return_table = self._create_refresh_view(
                self.model.primary_foreign_key)
        cursor.execute(f'DROP FUNCTION IF EXISTS {self.init_function_name};')
        cursor.execute(
            f'DROP FUNCTION IF EXISTS {self.init_function_name}(_id INT);')
        cursor.execute(f'DROP VIEW IF EXISTS {self.get_view_name};')
        try:
            dblogger.info(f"Preparing get_view sql statements for model {self.model.__name__}")
            cursor.execute(self.get_view)
            dblogger.info(f"- Prepared!")
        except UndefinedColumn as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed get_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing get_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedTable as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed get_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing get_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedObject as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed get_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing get_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except ProgrammingError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed get_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing get_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')
        except OperationalError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed get_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing get_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')

        try:
            dblogger.info(f"Preparing init_view sql statements for model {self.model.__name__}")
            cursor.execute(self.init_view)
            dblogger.info(f"- Prepared!")
        except UndefinedColumn as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed init_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing init_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedTable as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed init_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing init_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedObject as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed init_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing init_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except ProgrammingError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed init_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing init_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')
        except OperationalError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed init_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing init_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')

        try:
            dblogger.info(f"Preparing refresh_view sql statements for model {self.model.__name__}")
            cursor.execute(self.refresh_view)
            dblogger.info(f"- Prepared!")
        except UndefinedColumn as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed refresh_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing refresh_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedTable as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed refresh_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing refresh_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except UndefinedObject as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed refresh_view prepare statements for model {self.model.__name__} with {type.__name__}. Did you create tables?")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing refresh_view statements for model {self.model.__name__}')
            logger.error(f'- Did you create tables? Ignoring and continuing')
        except ProgrammingError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed refresh_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing refresh_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')
        except OperationalError as e:
            type, value, tb = sys.exc_info()
            dblogger.error(f"Failed refresh_view prepare statements for model {self.model.__name__} with {type.__name__}!")
            dblogger.error(f'- Specifically, {value}')
            dblogger.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
            logger.error(f'Caught Database error {value} while preparing refresh_view statements for model {self.model.__name__}')
            logger.error(f'- Ignoring and continuing')

    def clear(self):
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM "{self.model._meta.db_table}";')
        cursor.close()
    def load(self):
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {self.init_function_name}();')
        cursor.close()
    def refresh(self):
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM "{self.model._meta.db_table}"')
        cursor.execute(f'SELECT * FROM {self.init_function_name}();')
        cursor.close()
    def _create_get_view(self,source_model):
        """This creates the root materialized view query. The output here
        goes directly into the fields of the materialized view tables. These
        fields come from joins of other tables. Joins are the cause of
        database query slowdown, as each join means traversing more tables and
        indexes. Storing those fields into the materialized view table means
        you don't have to do the joins when you read the table instead of doing
        a query.
        """
        get_view_name = f'get_{self.model.__name__}_view'
        sql = (
            f'CREATE OR REPLACE VIEW\n {get_view_name}\n'
            f'AS\n{self._create_get_sql(source_model)};')
        return sql, get_view_name
    def get_view(self):
        if hasattr(self.model,'primary_foreign_key'):
            primary_foreign_key = self.model.primary_foreign_key
        else:
            primary_foreign_key = None
        get_view_name = f'get_{self.model.__name__}_view'
        sql = (
            f'CREATE OR REPLACE VIEW\n {get_view_name}\n'
            f'AS\n{self._create_get_sql(primary_foreign_key)};')
        return sqlparse.format(
            sql,
            reindent=True,
        )
    def _create_get_sql(self,source_model):
        """This creates the actual SELECT query statement used to build the
        materialized view. Each materialized view field has a 'source' variable
        the supplies the field. The 'source' variable can be a query string or
        a query expression.
        
        There are three types of special fields that are used in the output
        select view to filter out invalid data. This includes an Active bit
        field, a Start Time field, and a Stop Time field. Each of these fields
        are calculated based on a set of input fields. These input fields
        are given conditions that are used to calculate the output field.
        
        Active bit fields by default are required to be TRUE or NULL to be
        active. If a '-' is specified in front of the input field, then
        the input field should be FALSE instead of TRUE. If there is an '!'
        at the end of the input field, then the field can't be null. If the
        input field is something besides a boolean, then any not-null value
        is TRUE.

        materializedviews.ActiveBitField(
            active_conditions = [
                'model__field', # Field on model must be TRUE or NULL
                '-field', # Field on current model must be FALSE or NULL
                'field!', # Field on current model must be TRUE and NOT NULL
                '-field!', # Field on current model must be FALSE and NOT NULL
                ]
                
        DateTime start fields calculate when a model start time is valid
        based on a list of input fields. All fields must meet the minimum start
        time for field to be active.
        
        materializedviews.StartTimeField(
            start_conditions=[
                'field', # DateTimefield on current model to indicate start time
                'model__field', # DateTimefield on model to indicate start time
                ]

        DateTime stop fields calculate when a model expires based on a list of
        input fields. If any current time is past any expired time, then the
        model is invalid.
        
        materializedviews.StopTimeField(
            start_conditions=[
                'field', # DateTimefield on current model to indicate start time
                'model__field', # DateTimefield on model to indicate start time
                ]
        """
        query_fields = {}
        for field in self.model._meta.get_fields():
            field_name = get_view_field_name(self,field)
            if hasattr(field,'source'):
                if field.source:
                    if isinstance(field.source, str):
                        query_fields[f'{field_name}'] = F(field.source)
                    else:
                        query_fields[f'{field_name}'] = field.source
            # Process ActiveBitField
            if hasattr(field,'active_conditions'):
                queries = []
                for condition_field in field.active_conditions:
                    if condition_field[0] == '-':
                        condition_field = condition_field[1:]
                        if condition_field[-1] == '!':
                            condition_field = condition_field[:-1]
                            bitfield = getattr(self.model,
                                condition_field)
                            if isinstance(bitfield,models.BooleanField):
                                q = {condition_field:False}
                                queries.append(Q(**q))
                            else:
                                q = {condition_field+'__isnull':True}
                                queries.append(Q(**q))
                        else:
                            q1 = {condition_field+'__isnull':True}
                            q2 = {condition_field:False}
                            queries.append(Q(Q(**q1)|Q(**q2)))
                    else:
                        if condition_field[-1] == '!':
                            condition_field = condition_field[:-1]
                            bitfield = getattr(self.model,
                                condition_field)
                            if isinstance(bitfield,models.BooleanField):
                                q = {condition_field:True}
                                queries.append(Q(**q))
                            else:
                                q = {condition_field+'__isnull':False}
                                queries.append(Q(**q))
                        else:
                            q1 = {condition_field+'__isnull':True}
                            q2 = {condition_field:True}
                            queries.append(Q(Q(**q1)|Q(**q2)))
                reduced = reduce((lambda x, y: x & y),queries)
                added_field = ExpressionWrapper(
                    Q(reduced),output_field=models.BooleanField())
                query_fields[f'{field_name}'] = added_field
            # Process StartTimeField
            if hasattr(field,'start_conditions'):
                queries = []
                for condition_field in field.start_conditions:
                    t = {condition_field:None}
                    q = Case(
                        When(
                            Q(**t),
                            then=ExpressionWrapper(
                                Value("'-Infinity'"),models.DateTimeField())
                        ),
                        default=F(condition_field),
                        output_field=models.DateTimeField()
                    )
                    queries.append(q)
                added_field = Func(*queries,function='GREATEST')
                query_fields[f'{field_name}'] = added_field
            # Process StopTimeField
            if hasattr(field,'stop_conditions'):
                queries = []
                for condition_field in field.stop_conditions:
                    t = {condition_field:None}
                    q = Case(
                        When(
                            Q(**t),
                            then=ExpressionWrapper(
                                Value("'Infinity'"),
                                models.DateTimeField())
                        ),
                        default=F(condition_field),
                        output_field=models.DateTimeField()
                    )
                    queries.append(q)
                added_field = Func(*queries,function='LEAST')
                query_fields[f'{field_name}'] = added_field
        q = self.model._meta.get_field(
            source_model).remote_field.model.objects.values(**query_fields)
        return q.query.__str__()
    def get_sql(self):
        if hasattr(self.model,'primary_foreign_key'):
            primary_foreign_key = self.model.primary_foreign_key
        else:
            primary_foreign_key = None
        sql = self._create_get_sql(primary_foreign_key)
        return sqlparse.format(
            sql,
            reindent=True,
        )

    def _create_insert_sql(self,table_name,view_name):
        sql = [f'INSERT INTO\n  "{table_name}"\n (\n']
        source_fields = []
        destination_fields = []
        for field in self.model._meta.get_fields():
            field_name = get_field_name(self,field)
            active_field = False
            view_field_name = get_view_field_name(self, field)
            if hasattr(field,'source'):
                if field.source:
                    active_field = True
            if hasattr(field,'active_bit') \
                or hasattr(field,'start_time') \
                or hasattr(field,'stop_time'):
                active_field = True
            if active_field == True:
                destination_fields.append(f'  {field_name}')
                source_fields.append(
                        f'  "t"."{view_field_name}" "{field_name}"')
            if hasattr(field,'dirty_bit'):
                destination_fields.append(f'  {field_name}')
                source_fields.append('  FALSE')
        sql.append(',\n'.join(destination_fields) +
            '\n )\n SELECT\n' + ',\n'.join(source_fields))
        sql.append(f'\n FROM\n  {view_name} "t"')
        return ''.join(sql)
    def get_insert_sql(self):
        get_view_name = f'get_{self.model.__name__}_view'
        table_name = self.model._meta.db_table
        sql = self._create_insert_sql(table_name,get_view_name)
        return sqlparse.format(
            sql,
            reindent=True,
        )
    def _create_init_view(self):
        init_view_name = f'init_{self.model.__name__}_view'
        get_view_name = f'get_{self.model.__name__}_view'
        table_name = self.model._meta.db_table
        return f'CREATE OR REPLACE FUNCTION\n  {init_view_name}()\n' \
            f'RETURNS\n  "{table_name}"\nSECURITY DEFINER\n' \
            f'LANGUAGE sql AS\n$$\n' \
            f'{self._create_insert_sql(table_name,get_view_name)}\n' \
            f' RETURNING "{table_name}".*;\n$$;', init_view_name, table_name
    def get_init_view(self):
        sql, init_view_name, table_name = self._create_init_view()
        return sqlparse.format(
            sql,
            reindent=True,
        )
    def _create_update_sql(self,get_view_name,key,key_field):
        table_name = self.model._meta.db_table
        sql = [f'UPDATE\n  "{table_name}"\nSET\n']
        fields = []
        for field in self.model._meta.get_fields():
            field_name = get_field_name(self,field)
            active_field = False
            if hasattr(field,'source'):
                if field.source:
                    active_field = True
            if hasattr(field,'active_bit') \
                or hasattr(field,'start_time') \
                or hasattr(field,'stop_time'):
                active_field = True
            if active_field == True:
                fields.append(
                    f'  {field_name} = t.{field_name}'
                    f'{self.material_view_field_id}')
            if hasattr(field,'dirty_bit'):
                fields.append(f'  {field_name} = FALSE')
        sql.append(',\n'.join(fields) + f'\nFROM (\n')
        where = [f'"{table_name}"."{key_field}" = {key}']
        if hasattr(self.model,'unique_select_fields'):
            for wherefield in self.model.unique_select_fields:
                w = self.model._meta.get_field(wherefield)
                w_name = get_field_name(self,w)
                where.append(
                    f'"{table_name}"."{w_name}" = t.{w_name}'
                    f'{self.material_view_field_id}')
        where_clause = '\n AND '.join(where)

        id_parameters = [
            f'"u"."{key_field}{self.material_view_field_id}"'
            f' = {key}']
        if hasattr(self.model,'unique_select_fields'):
            for uniqueid_field in self.model.unique_select_fields:
                i = self.model._meta.get_field(uniqueid_field)
                i_name = get_field_name(self,i)
                id_parameters.append(
                    f'"u"."{i_name}{self.material_view_field_id}"'
                    f' = {i_name}{key}'
                )
        id_parameters_clause = '\n  AND '.join(id_parameters)

        sql.append(f' SELECT\n  *\n FROM\n  {get_view_name} AS "u"\n '
            f'WHERE\n  {id_parameters_clause}\n'
            f') t\nWHERE\n {where_clause}')
        return ''.join(sql)
    def _create_refresh_view(self, key_field):
        refresh_view_name = f'refresh_{self.model.__name__}_view'
        get_view_name = f'get_{self.model.__name__}_view'
        table_name = self.model._meta.db_table

        id_parameters = [f'{foreign_key_id} int']
        if hasattr(self.model,'unique_select_fields'):
            for uniqueid_field in self.model.unique_select_fields:
                i = self.model._meta.get_field(uniqueid_field)
                i_name = get_field_name(self,i)
                id_parameters.append(
                    f'{i_name}{foreign_key_id} int')
        id_parameters_clause = ',\n    '.join(id_parameters)


        return (f'CREATE OR REPLACE FUNCTION\n'
            f'  {refresh_view_name}(\n    {id_parameters_clause}\n  )\n'
            f'RETURNS\n  "{table_name}"\nSECURITY DEFINER\n'
            f'LANGUAGE sql AS\n$$\n'
            f'{self._create_update_sql(get_view_name,foreign_key_id,key_field)}'
            f'\nRETURNING'
            f' "{table_name}".*;\n$$;', refresh_view_name, table_name)
    def get_refresh_view(self):
        sql, refresh_view_name, table_name = self._create_refresh_view(self.model.primary_foreign_key)
        return sql
class MaterializedViewModel(models.Model):
    objects = MaterializedViewManager()
    class Meta:
        abstract = True
