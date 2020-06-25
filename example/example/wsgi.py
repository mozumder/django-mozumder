"""
WSGI config for example project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys
import mozumder

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')
sys.path.insert(0, mozumder.__path__)

application = get_wsgi_application()

