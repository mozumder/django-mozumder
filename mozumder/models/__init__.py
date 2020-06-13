from .logging import *
from django.utils.text import slugify as django_slugify

def slugify(text):
    return django_slugify(text.replace(" & ", " and ").replace(" + ", " and "))
