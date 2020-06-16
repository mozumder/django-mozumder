from django.apps import apps
from django.apps import AppConfig
from django.db import connection
from django.conf import settings
import multiprocessing
from django.db.backends.signals import connection_created

from mozumder.apps import PreparedAppConfig

from .utilities.logger import LogWriter
from .signals import log_response

try:
    import uwsgi
    import uwsgidecorators
    uwsgi_mode = True
except:
    uwsgi_mode = False

import logging
message_log = logging.getLogger("django")

class AnalyticsConfig(PreparedAppConfig):
    name = 'analytics'
    verbose_name = "Logging & Analytics"
    dbConnectSignal = 'prepareAnalyticsDb'

    sql_dirs = (
            'analytics/include/sql',
            )

    def db_connected(self,sender, connection, **kwargs):
        super().db_connected(sender, connection, **kwargs)
        lock = apps.get_app_config('unchained')._lock
        self.logwriter = LogWriter(self.cursor, lock)

        try:
            MULTIPROCESS = settings.MULTIPROCESS
        except:
            MULTIPROCESS = False
        if MULTIPROCESS:
            message_log.info('Multi process mode!')
            lock = multiprocessing.Lock()
            if uwsgi_mode:
                message_log.info('UWSGI mode!')
                log_response.connect(self.logwriter.log_uwsgi, dispatch_uid="log_response")
            else:
                message_log.info('Runserver mode =^(')
                log_process = multiprocessing.Process(name='Logging', target=LogWriter.log_process_listener, args=(LogWriter.e,LogWriter.q))
                log_process.daemon=True
                log_process.start()
                log_response.connect(self.logwriter.log_multiprocess, dispatch_uid="log_response")
        else:
#            message_log.debug('Single Processor mode =^(')
            log_response.connect(self.logwriter.log, dispatch_uid="log_response")
