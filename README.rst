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

In here, let's create a couple of Django apps:

::

    ./manage.py add_app fashion
    ./manage.py add_app images


And for each app, we can start to create our database models. Each model takes a list of field arguments:

::

    ./manage.py add_model fashion Collection  \
        cover_photo:ForeignKey:re:Photo:CASCADE:related_name=cover_photo \
        social_photo:ForeignKey:re:Photo:CASCADE:related_name=social_photo \
        title:CharField:rel:255 \
        author:ForeignKey:rel:Person:CASCADE \
        description:TextField:re \
        album:ForeignKey:re:Album:CASCADE \
        season:ForeignKey:rel:Season:CASCADE \
        rating:SmallIntegerField:rel:0 \
        date_created:DateTimeField:rA \
        date_published:DateTimeField:re-i \
        date_modified:DateTimeField:ra \
        date_expired:DateTimeField:re-i \
        date_deleted:DateTimeField:re-i
    ./manage.py add_model fashion Person  \
        first_name:CharField:reL:50 \
        last_name:CharField:rel:50
    ./manage.py add_model fashion Brand  \
        name:CharField:reL:50
    ./manage.py add_model fashion Season  \
        name:CharField:reL:50
    ./manage.py add_model fashion Album looks:ManyToManyField:re:Look
    ./manage.py add_model fashion Look  \
        collection:ForeignKey:re:Collection:CASCADE \
        name:CharField:reL:50 \
        rating:SmallIntegerField:rel:0
    ./manage.py add_model fashion View  \
        photo:ForeignKey:re:Photo:CASCADE \
        type:ForeignKey:re:ViewTypes:CASCADE
    ./manage.py add_model fashion ViewTypes  \
        name:CharField:reL:50 \
        code:CharField:re:2

    ./manage.py add_model images Image  \
        width:PositiveIntegerField:re \
        height:PositiveIntegerField:re \
        file:ImageField:re
    ./manage.py add_model images Photo  \
        original:ForeignKey:re:Image:CASCADE:related_name=original_file \
        small:ForeignKey:re:Image:CASCADE:related_name=small_file \
        medium:ForeignKey:re:Image:CASCADE:related_name=medium_file \
        large:ForeignKey:re:Image:CASCADE:related_name=large_file \
        thumbnail:ForeignKey:re:Image:CASCADE:related_name=thumbnail_file

We can now write the apps with the build command:

::

    ./manage.py build

This creates the apps models along with admin and template components. In addition, this adds the app to the INSTALLED_APPS settings.py configuration, as well as adding the apps urls to the project urls.py.

From here, we continue with the usual Django development process of creating migration files and running the migrations in order to create the database schema:

::

    ./manage.py makemigrations
    ./manage.py migrate
    ./manage.py createsuperuser

At this point, you can contine with the usual Django development of your app by editing your models and creating templates. You may also want to edit the urls.py file to adjust which urls you want active in your app.
