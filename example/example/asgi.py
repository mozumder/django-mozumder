"""
ASGI config for example project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import sys
import mozumder
import inspect

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')
sys.path.insert(0, os.path.dirname(inspect.getfile(mozumder)))

application = get_asgi_application()

