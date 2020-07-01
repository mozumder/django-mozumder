import os
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

import mozumder

class Command(BaseCommand):

    help = 'Modify Django Settings and URLs to enable an app.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            'app',
            action='store',
            help='App name',
            )
        parser.add_argument(
            'model',
            action='store',
            help='Model name',
            )
        parser.add_argument(
            'file',
            action='store',
            help='CSV file name',
            )
            
    def handle(self, *args, **options):

        csv.reader(
        with open(options['file'], "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in csvreader
                
        output = ''
        state = 'file'
        for line in f.readlines():
            if state == 'file':
                if line == 'INSTALLED_APPS = [\n':
                    state = 'INSTALLED_APPS'
            elif state == 'INSTALLED_APPS':
                if line == ']\n':
                    output += f"    '{app_name}',\n"
                    state = 'file'
            output += line
        f.close()
        f = open(settings_file, "w")
        f.write(output)
        f.close()

