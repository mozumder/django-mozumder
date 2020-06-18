import os

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'Start a new django-mozumder project.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            'name',
            action='store',
            help='Project Name',
            )
            
    def handle(self, *args, **options):

        path = os.getcwd() + '/' + options['name']
        access_rights = 0o755

        try:
            os.mkdir(path, access_rights)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)
