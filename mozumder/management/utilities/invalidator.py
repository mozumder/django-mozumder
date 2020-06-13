import logging
import pprint

import select
import psycopg2
import psycopg2.extensions

from django.core.cache import cache
from django.conf import settings

pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger("cache")

class CacheInvalidator:

    # Database Tables for triggers
    trigger_lookup = [
    ]

    #
    # This is insane.  Trying to figure out what cache items to delete,
    # based on Postgres notifications
    #
    redis_lookup = {
    }

    operation_lookup = [
        'Insert',
        'Update',
        'Delete',
    ]

    @staticmethod
    def listen():
    
        views = [
        ]

        materialized_views = {}
        blocks = {}
        for view in views:
            
            if view.view_function.model.__name__ in materialized_views.keys():
                page_table_views = materialized_views[view.view_function.model.__name__]
            else:
                page_table_views = {}

            if view.view_function.get_args:
                page_table_views[view.__class__.__name__] = list(view.view_function.get_args.keys())
                materialized_views[view.view_function.model.__name__] = page_table_views

            if hasattr(view,'get_template'):
                for block in view.get_template.blocks:
                    if hasattr(block,'view_function'):
                        block_table = block.view_function.model.__name__
                    else:
                        block_table = view.view_function.model.__name__

                    if block_table in materialized_views.keys():
                        block_views = materialized_views[block_table]
                    else:
                        block_views = {}

                    if block.vary:
                        block_views[block.cache_key] = block.vary
                    else:
                        if block.context_vary:
                            block_views[block.cache_key] = []

                    materialized_views[block_table] = block_views
#                    print(f'{view.__class__.__name__} {view.get_template.__class__.__name__} {block.__class__.__name__} {block.cache_key}')

#        pp.pprint(materialized_views)

        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (settings.DATABASES['default']['HOST'], settings.DATABASES['default']['NAME'], settings.DATABASES['default']['USER'], settings.DATABASES['default']['PASSWORD'], )

        conn = psycopg2.connect(conn_string)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        curs = conn.cursor()
        curs.execute("listen cache;")

#        print("Waiting for Postgres notifications on channel 'cache'")
        logger.info("Waiting for Postgres notifications on channel 'cache'")

        notifications = set()
        while 1:
            if select.select([conn],[],[],1) != ([],[],[]):
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
#                    if settings.BENCHMARK:
                    logger.debug("Got channel notification: %s" % notify.payload)
                    notifications.add(notify.payload)
            
            #
            # To do: Need to run this in a separate process as well
            # to avoid missing notifications while this is running
            #
            if notifications:
                cache_keys = set()
                all_pages = set()
                cover_pages = set()
                season_pages = set()
                collection_pages = set()
                latest_pages = set()
                index_pages = set()

                all = False
                for notification in notifications:
                    cover = False
                    season = False
                    collection = False
                    latest = False
                    index = False
                    keys = notification.split(":")
                    table = keys[0]
                    if len(keys) > 1:
                        field1 = keys[1]
                        id1 = keys[2]
                    else:
                        field1 = None
                        id1 = None
                    if len(keys) > 3:
                        field2 = keys[3]
                        id2 = keys[4]
                    else:
                        field2 = None
                        id2 = None

                    if table in materialized_views:
                        keys = materialized_views[table]
                        if keys:
                            for key in keys:
                                fields = keys[key]
                                delete_key = None
                                if fields == []:
                                    delete_key = f'{key}'
                                elif fields[0] == field1:
                                    delete_key = f'{key}:{id1}'
                                elif fields[0] == field2:
                                    delete_key = f'{key}:{id2}'
                                if delete_key:
                                    cache_keys.add(delete_key)

                if cache_keys:
                    result = cache.delete_many(cache_keys)
                    logger.info("  Deleted %i Cache items" % len(cache_keys))
                    for key in cache_keys:
                        logger.debug("  - %s" % key)
                notifications = set()


