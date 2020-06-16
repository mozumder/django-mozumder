===============
django-mozumder
===============

djang-mozumder is a Django app containing various utilities to enhance Django. This includes a templating system based on Python, updated views that compress the cache to effectively increase cache size by 10x and page generation times, a system to manage materialized views to reduce page generation times, as well as logging & analytics and internationaliztion & localization (i18n/l10n) utility models.

Quick setup
-----------

1. Add "mozumder" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'mozumder',
        'anayltics', # Optional logging views
        'i18n', # Optional internationalization/localization models
        ...
    ]

2. Run ``python manage.py migrate`` to create the database models for logging and i18n/l10n.
