===============
django-mozumder
===============

django-mozumder is a Django app containing various utilities to enhance Django with Postgresql and Redis that have reduced page generation times from 1-2 seconds down to the 1-2 milliseconds range, speeding up a website by 1000x.

This includes a templating system based on Python instead of Django's pseudo-HTML or Jinja that also automates HTTP Content Security Policy directives, updated views that use Postgres prepared statements tied with a system to manage materialized views to speed up database queries, and a Zlib compressed cache response generator that uses pre-compressed template blocks to eliminate page compression stage while effectively increasing cache size by 10x.

Postgresql prepared statements reduce database access times by about 15ms per query. Materialized views eliminate JOINS in SQL queries, saving about 10ms per table lookup. Precompressed Zlib compressed cache eliminate the Gzip page compression step of each page request, saving about 10ms per page.

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
    
4. From here, you create database models with materialized views, template components in Python, and views that use prepared statements.

========
Tutorial
========

Let's start with a Django Blogging app that includes the following models:

::

    class Article(models.Model):
        cover_photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
        headline = models.CharField(max_length=255)
        author = models.ForeignKey('Person', on_delete=models.CASCADE)
        body = models.TextField()

    class Person(models.Model):
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)

    class Photo(models.Model):
        original = models.ForeignKey('Photo', related_name='original_file', on_delete=models.CASCADE)
        small = models.ForeignKey('Photo', related_name='small_file', on_delete=models.CASCADE)
        medium = models.ForeignKey('Photo', related_name='medium_file', on_delete=models.CASCADE)
        large = models.ForeignKey('Photo', related_name='thumbnail_file', on_delete=models.CASCADE)
        thumbnail = models.ForeignKey('Photo', related_name='original_file', on_delete=models.CASCADE)

    class ImageFile(models.Model):
        width = models.PositiveIntegerField()
        height = models.PositiveIntegerField()
        file = models.ImageField()


Python-based Templates
----------------------

Materialized Views
------------------

Postgres Prepared Statements
----------------------------

Zlib compressed cache
---------------------

