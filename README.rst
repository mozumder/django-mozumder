===============
django-mozumder
===============

django-mozumder is a set of utilities to enhance Django with Postgres and Redis. It was designed to serve a celebrity-oriented website that sees bursts of web traffic. The goal was to reduce non-cached page generation times from 1-2 seconds down to the 1-2 milliseconds range on a single CPU core, speeding up a Django site by 1000x. See `Django Unchained at FutureClaw <https://www.mozumder.net/blog/django-unchained-how-futureclaw-serves-pages-in-microseconds>`_

Python-based Templates
----------------------

The first change is a new component-based templating system built directly with Python instead of through Django's pseudo-HTML templates (or Jinja templates). This component-based template system handles CSS and JS minification, as well as precomputing HTTP Content-Security-Policy header hashes, improving security.


Prepared Statements and Compressed Views
----------------------------------------

The next major change is a new view system that uses Postgres prepared statements. Postgres prepared statements are pre-compiled SQL queries that eliminate parsing, compiling, and query optimization steps on each SQL query. This saves about 15ms per query.  Additionaly, these new views ties in with the new component-based templates to compress template components before caching. This effectively increases the cache size by 10x, and eliminates the Gzip compression step on page reads through a new response generator. This saves an addition 10-15ms per page read.

Materialized View Models
------------------------

The final major change are tools to faciliate database materialized view models, including generating prepared statements from new materialized model fields and cache invalidation for live updating of materialized view models. Materialized views are database models that pre-render elements of the view into database fields. For example, database joins can be eliminated by storing joined fields into a table. Eliminating SQL JOIN statements can save another 15ms or so for each join on a decent sized table.

Logging & Internationalization
------------------------------

Also included are apps for database logging, to speed up the site by eliminating the need for third-party logging & analytics Javascript, as well as an app for internationalization and localization (i18n/l11n) models to faciliate multi-lingual sites.

===========
Quick setup
===========

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
    
4. From here, you create database models with materialized views, template components in Python, and views that use prepared statements.

========
Tutorial
========

Let's start a new project with the ``mozumder-admin`` command:


::

    mozumder-admin startproject \
        --db_url postgresql://exampleuser:examplepw@localhost/example \
        --db_admin_url postgresql://adminuser:adminpw@localhost/example \
        --domainname example.com \
        --hostname www.example.com \
        --create_db --create_venv example

This creates a project directory with everything needed to deploy the project, including a full Python virtualenv.

Let's go into it and source the virtualenve:

::

    cd example
    source venv.example/bin/activate

And start an app for the project using the traditional Django startapp command:

::

    ./manage.py startapp old_fashion

We have to update our app project directory with some new files and directories to work with django-mozumder

::

    ./manage.py prepareoldapp old_fashion

And now, we get to the meat of our app by using the ``addmodel`` command to create our database models. Each model takes a lis of field arguments, with :

::

    ./manage.py addmodel --list_display id --old old_fashion Collection  \
        *_cover_photo:ForeignKey:Photo:CASCADE:related_name=cover_photo \
        *_social_photo:ForeignKey:Photo:CASCADE:related_name=social_photo \
        *_title*:CharField:max_length=255 \
        *_author*:ForeignKey:Person:CASCADE \
        *_description:TextField \
        *_album:ForeignKey:Album:CASCADE \
        *_season*:ForeignKey:Season:CASCADE \
        *_rating*:SmallIntegerField:default=0 \
        *date_created:DateTimeField:auto_now_add=True \
        *_date_published:DateTimeField:null=True:blank=True:db_index=True \
        *date_modified:DateTimeField:auto_now=True \
        *_date_expired:DateTimeField:null=True:blank=True:db_index=True \
        *_date_deleted:DateTimeField:null=True:blank=True:db_index=True

    ./manage.py addmodel --detail_display id --old old_fashion Person  \
        *_first_name**:CharField:max_length=50 \
        *_last_name*:CharField:max_length=50
    ./manage.py addmodel --detail_display id --list_display id --old old_fashion Brand  \
        *_name**:CharField:max_length=50
    ./manage.py addmodel --list_display id --old old_fashion Season  \
        *_name**:CharField:max_length=50
    ./manage.py addmodel --list_display id --old old_fashion Album  \
        *_looks:ManyToManyField:Look
    ./manage.py addmodel --list_display id --old old_fashion Look  \
        *_collection:ForeignKey:Collection:CASCADE \
        *_name**:CharField:max_length=50 \
        *_rating*:SmallIntegerField:default=0
    ./manage.py addmodel --list_display_links id --old old_fashion View  \
        *_photo:ForeignKey:Photo:CASCADE \
        *_type:ForeignKey:ViewTypes:CASCADE
    ./manage.py addmodel --list_display id --old old_fashion ViewTypes  \
        *_name**:CharField:max_length=50 \
        *_code:CharField:max_length=2
    ./manage.py addmodel --list_display_links id --old old_fashion Photo  \
        *_original:ForeignKey:Photo:CASCADE:related_name=original_file \
        *_small:ForeignKey:Photo:CASCADE:related_name=small_file \
        *_medium:ForeignKey:Photo:CASCADE:related_name=medium_file \
        *_large:ForeignKey:Photo:CASCADE:related_name=large_file \
        *_thumbnail:ForeignKey:Photo:CASCADE:related_name=thumbnail_file
    ./manage.py addmodel --list_display_links id --old old_fashion Image  \
        *_width:PositiveIntegerField \
        *_height:PositiveIntegerField \
        *_file:ImageField

This creates the apps models along with admin and template components.

We can now enable the app with the enableapp command:

::

    ./manage.py enableapp old_fashion

This adds the app to the INSTALLED_APPS settings.py configuration, as well as adding the apps urls to the urls.py.

From here, we continue with the usual Django development process of creating migration files and running the migrations in order to create the database schema:

::

    ./manage.py makemigrations
    ./manage.py migrate

At this point, you can contine with the usual Django development of your app by editing your models and creating templates. You may also want to edit the urls.py file to adjust which urls you want active in your app.
