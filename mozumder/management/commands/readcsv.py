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
            help='CSV file name. First line is a header line with all the field names.',
            )
            
    def handle(self, *args, **options):
        module = __import__(options['app'] + '.models')
        class_ = getattr(getattr(module,'models'), options['model'])
        
        fields = {}
        with open(options['file'], "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if row:
                    i = 0
                    if fields == {}:
                        field_lookup =[]
                        for field in row:
                            field_lookup.append(row[i])
                            fields[field] = ''
                            i = i + 1
                    else:
                        for field in row:
                            fields[field_lookup[i]] = field
                            i = i + 1
                        _, created = class_.objects.get_or_create(**fields)
                

