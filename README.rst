===============
django-mozumder
===============

django-mozumder is a Django app containing various utilities to enhance Django with Postgres and Redis. This includes a templating system based on Python, updated views that compress the cache to effectively increase cache size by 10x and page generation times, a system to manage materialized views to reduce page generation times, as well as logging & analytics and internationaliztion & localization (i18n/l10n) utility models.

Quick setup
-----------

Requirements: Have Python 3.8, Postgres, and Redis installed.

1. Install package using ``pip``

::

    $ pip install django-mozumder

2. Create project directory structure with ``mozumder-admin``

::

    $ mozumder-admin --db_url postgresql://db_username:db_password@db_hostname/db_databasename --domainname example.com --hostname www.example.com startproject --create_db mysite

3. In your project, create the database tables for logging and i18n/l10n using the migrate command:

::

    $ ./manage.py migrate


