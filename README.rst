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

Let's start with a Django fashion app that includes the following models:

::

    class Collection(models.Model):
        cover_photo = models.ForeignKey('Photo', related_name='cover_photo', on_delete=models.CASCADE)
        social_photo = models.ForeignKey('Photo', related_name='social_photo', on_delete=models.CASCADE)
        title = models.CharField(max_length=255)
        author = models.ForeignKey('Person', on_delete=models.CASCADE)
        description = models.TextField()
        album = models.ForeignKey('Album', on_delete=models.CASCADE)
        season = models.ForeignKey('Season', on_delete=models.CASCADE)
        rating = models.SmallIntegerField(default=0)
        date_created = models.DateTimeField(auto_now_add=True)
        date_published = models.DateTimeField(null=True, blank=True,db_index=True,)
        date_modified = models.DateTimeField(auto_now=True)
        date_expired = models.DateTimeField(null=True, blank=True,db_index=True,)
        date_deleted = models.DateTimeField(null=True, blank=True,db_index=True,)

    class Person(models.Model):
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)

    class Brand(models.Model):
        name = models.CharField(max_length=50)

    class Season(models.Model):
        name = models.CharField(max_length=50)

    class Album(models.Model):
        looks = models.ManyToManyField('Look')

    class Look(models.Model):
        view = models.OneToManyField('View')
        name = models.CharField(max_length=50)
        rating = models.SmallIntegerField(default=0)
        
    class View(models.Model):
        photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
        type = models.ForeignKey('ViewTypes', on_delete=models.CASCADE)

    class ViewTypes(models.Model):
        name = models.CharField(max_length=50)
        code = models.CharField(max_length=2)

    class Photo(models.Model):
        original = models.ForeignKey('Photo', related_name='original_file', on_delete=models.CASCADE)
        small = models.ForeignKey('Photo', related_name='small_file', on_delete=models.CASCADE)
        medium = models.ForeignKey('Photo', related_name='medium_file', on_delete=models.CASCADE)
        large = models.ForeignKey('Photo', related_name='large_file', on_delete=models.CASCADE)
        thumbnail = models.ForeignKey('Photo', related_name='thumbnail_file', on_delete=models.CASCADE)

    class Image(models.Model):
        width = models.PositiveIntegerField()
        height = models.PositiveIntegerField()
        file = models.ImageField()


.. tutorial currently under development
