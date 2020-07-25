from django.core.management.base import BaseCommand
from django.conf import settings
from ..utilities.modelwriter import *

class Command(BaseCommand):

    help = 'Add a new model to an app.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            action='store',
            help='App name',
            )
    def handle(self, *args, **options):
        context={
            'app_name': options['app_name'],
        }
        ModelsFile().write(context)


