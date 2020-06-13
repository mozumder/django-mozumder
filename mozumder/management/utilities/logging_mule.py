import logging
import threading

from django.db import connection
import psycopg2
from uwsgi import mule_get_msg

from mozumder.management.utilities.logger import LogWriter

logger = logging.getLogger("django")

_lock=threading.Lock()
cursor = connection.cursor().connection.cursor(
    cursor_factory=psycopg2.extras.NamedTupleCursor)

def listener():
    global cursor
    global lock
    logwriter = LogWriter(
        cursor=cursor,
        lock=_lock
    )
    logger.info("uWSGI Log Mule Process started & listening")
    while True:
        msg = mule_get_msg()
        logwriter.threaded_write(msg)

if __name__ == '__main__':
    listener()
