"""
Django settings for example project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from decouple import config, Csv

PROJECT_NAME = 'example'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY',default='')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG',default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mozumder',
    'mozumder.analytics',
    'mozumder.i18n',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'example.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'HOST': config('DB_HOST',default='localhost'), # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': config('DB_PORT',default=''), # Set to empty string for default.
        'NAME': config('DB_NAME'), # Or path to database file if using sqlite3.
        'USER': config('DB_USERNAME'),
        'PASSWORD': config('DB_PASSWORD'),
        'CONN_MAX_AGE': None,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'log': {
            'format': '%(asctime)s.%(msecs)02d %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s: %(message)s',
        },
        'raw': {
            'format': '%(message)s',
        },
        'debug': {
            'format': '%(asctime)s.%(msecs)02d %(levelname)s: (%(module)-10s) %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'message': {
            'format': '%(asctime)s.%(msecs)02d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'threaded': {
            'format': '%(asctime)s.%(msecs)02d | %(process)d: %(module)-10s (%(threadName)-10s) | %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/example.log',
            'formatter': 'log',
            'encoding': 'utf8',
        },
        'management': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'log/example.error.log',
            'formatter': 'threaded',
            'encoding': 'utf8',
        },
        'access_logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/example.access.log',
            'formatter': 'message',
            'encoding': 'utf8',
        },
        'cache_logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/example.cache.log',
            'formatter': 'message',
            'encoding': 'utf8',
        },
        'database_logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/example.db.log',
            'formatter': 'log',
            'encoding': 'utf8',
        },
        'mail': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/example.log',
            'formatter': 'message',
            'encoding': 'utf8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console','logfile'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'management': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_MANAGEMENT_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'analytics': {
            'handlers': ['console','access_logfile'],
            'level': os.getenv('DJANGO_ANALYTICS_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': True,
        },
        'cache': {
            'handlers': ['console','cache_logfile'],
            'level': os.getenv('DJANGO_CACHE_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': True,
        },
        'database': {
            'handlers': ['console','database_logfile'],
            'level': os.getenv('DJANGO_DB_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console','database_logfile'],
            'level': os.getenv('DJANGO_DB_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'mail': {
            'handlers': ['console','mail'],
            'level': os.getenv('DJANGO_MAIL_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': True,
        },
        'images': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_IMAGESAPP_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': True,
        },
    },
}


