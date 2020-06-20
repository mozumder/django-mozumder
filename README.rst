===============
django-mozumder
===============

django-mozumder is a Django app containing various utilities to enhance Django with Postgres and Redis. This includes a templating system based on Python, updated views that compress the cache to effectively increase cache size by 10x and page generation times, a system to manage materialized views to reduce page generation times, as well as logging & analytics and internationaliztion & localization (i18n/l10n) utility models.

Quick setup
-----------

Start with a Django project with a Postgres database and Redis cache.

1. Install package using ``pip``

::

    $ pip install django-mozumder

2. Create project directory structure

::

    $ mozumder-admin --db_url \
        postgresql://db_username:db_password@db_hostname/db_databasename startproject 

3. Add ``mozumder`` to your Django project's ``INSTALLED_APPS`` setting:

::

    INSTALLED_APPS = [
        ...
        'mozumder',
        'mozumder.analytics', # Optional logging views
        'mozumder.i18n', # Optional internationalization/localization models
        ...
    ]

4. In your Django project, create the database tables for logging and i18n/l10n using the migrate command:

::

    $ ./manage.py migrate


