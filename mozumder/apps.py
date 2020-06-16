import os
import sys
from subprocess import call
import logging
import inspect
import threading
import traceback
import multiprocessing

from django.apps import apps
from django.apps import AppConfig
from django.db import connection
from django.conf import settings
from django.db.backends.signals import connection_created
from django.db.utils import ProgrammingError, OperationalError
import psycopg2

db_log = logging.getLogger("database")
message_log = logging.getLogger("django")

class PreparedAppConfig(AppConfig):
    def execute_sql_files(self,command):
        pth = os.path.dirname(inspect.getmodule(self.__class__).__file__) + '/sql'
        if not hasattr(self, 'sql_dirs'):
            self.sql_dirs = [pth]
        for dir in self.sql_dirs:
            file_name = dir + '/' + command + '.sql'
            try:
                file = open(file_name, 'r')
            except FileNotFoundError:
                db_log.debug('No SQL file: %s' % file_name)
                pass
            except (OSError, IOError) as e:
                db_log.error('Error reading SQL file: %s' % file_name)
                raise e
            else:
                sql_commands=file.read().strip()
                if sql_commands:
                    cursor = connection.cursor()
                    try:
                        cursor.execute(sql_commands)
                        db_log.info(f"Executed statements from file {file_name}")
                    except (OperationalError, ProgrammingError) as e:
                        type, value, tb = sys.exc_info()
                        db_log.error(f"Failed running SQL command: {sql_commands}!")
                        db_log.error(f'- Specifically, {value}')
                        db_log.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
                        logger.error(f'Caught Database error {value} while trying to exectute sql file {file_name}')
                        logger.error(f'- Ignoring and continuing')
                    cursor.close()

    def read_prepared_statements(self):
        pth = os.path.dirname(inspect.getmodule(self.__class__).__file__) + '/include/sql/prepared_statements'
        if not hasattr(self, 'sql_dirs'):
            self.sql_dirs = [pth]
        for dir in self.sql_dirs:
            try:
                list_of_files = os.listdir(dir+'/prepared_statements')
            except:
                list_of_files = []
            for file_name in list_of_files:
                try:
                    file = open(dir+'/prepared_statements/'+file_name, 'r')
                except FileNotFoundError:
                    db_log.info('No SQL prepared statements file: %s' % file_name)
                    pass
                except (OSError, IOError) as e:
                    db_log.error('Error reading SQL prepared statements file: %s' % file_name)
                    raise e
                else:
                    sql_prepare=file.read().strip()
                    if sql_prepare:
                        cursor = connection.cursor()
                        try:
                            cursor.execute(sql_prepare)
                            db_log.info(f"Prepared statements from file {file_name}")
                        except (OperationalError, ProgrammingError) as e:
                            type, value, tb = sys.exc_info()
                            db_log.error(f"Failed preparing statements statements with {type.__name__}!")
                            db_log.error(f'- Specifically, {value}')
                            db_log.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
                            logger.error(f'Caught Database error {value} while trying to exectute sql file {file_name}')
                            logger.error(f'- Ignoring and continuing')
                        cursor.close()

    def db_connected(self, sender, connection, **kwargs):
        self.cursor = connection.cursor().connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor)
        app = apps.get_app_config(self.name)
        models_list= app.get_models()
        for model in models_list:

            model_bases = model.__bases__
            for base in model_bases:
                base_name = base.__name__
                if base_name == 'MaterializedViewModel':
                    try:
                        db_log.info(f"Preparing sql statements for model {model.__name__}")
                        model.objects.prepare(self.cursor)
                        db_log.info(f"- Prepared!")
                    except (OperationalError, ProgrammingError) as e:
                        type, value, tb = sys.exc_info()
                        db_log.error(f"Failed initial prepare statements for model {model.__name__} with {type.__name__}!")
                        db_log.error(f'- Specifically, {value}')
                        db_log.error("- Please review the most recent stack entries:\n" + "".join(traceback.format_list(traceback.extract_tb(tb, limit=5))))
                        message_log.error(f'Caught Database error {value} while preparing statements for model {model.__name__}')
                        message_log.error(f'- Ignoring and continuing')

        self.execute_sql_files('prepare')

        self.read_prepared_statements()
        if hasattr(settings, 'MATERIALIZED_VIEWS'):
            if settings.MATERIALIZED_VIEWS == True:
                self.execute_sql_files('prepare_materialized')

    def ready(self):
        connection_created.connect(self.db_connected, dispatch_uid=self.dbConnectSignal)


class MozumderAppConfig(PreparedAppConfig):
    name = 'Mozumder'
    verbose_name = 'Django Mozumder'
    dbConnectSignal = 'prepareMozumderDb'
    sql_dirs = (
            'mozumder/include/sql',
            )
    def db_connected(self,sender, connection, **kwargs):
        self._lock = threading.Lock()
        super().db_connected(sender, connection, **kwargs)

    def ready(self):
        """
        Each Mozumder app does the following upon startup:
          1. Minimize HTML, CSS, JS
          2. Read prepared SQL statements once database is connected
          3. Load templates into memory
        """

        if hasattr(self, 'dbConnectSignal'):
            connection_created.connect(self.db_connected, dispatch_uid=self.dbConnectSignal)
        if hasattr(self, 'Makefile'):
            message_log.debug('Running Make')
            result = call(["make","-j","8","-f", self.Makefile])
