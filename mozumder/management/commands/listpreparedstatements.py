from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.apps import AppConfig
from ...db.materializedviews.materializedviews import MaterializedViewModel
class Command(BaseCommand):

    help = 'Manage database prepared statements.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            'appname',
            action='store',
            nargs='?',
            default=None,
            help='App containing the models you want to list',
            )
        parser.add_argument(
            'modelname',
            action='store',
            nargs='*',
            default=None,
            help='Specific materialized view table to list (or all in app none selected)',
            )

    def handle(self, *args, **options):
        
        if options['modelname']:
            models = []
            for modelname in options['modelname']:
                models.append(apps.get_model(options['appname'], modelname))
        elif options['appname']:
            models = [model for model in apps.get_app_config(options['appname']
                ).get_models()]
        else:
            models = [model for model in apps.get_models()]
#        print('models:', models)

        for model in models:
            if issubclass(model,MaterializedViewModel):
                print(f'Showing prepared statements for model {model.__name__}'
                    f' (database table {model._meta.db_table})' )
                print(model.objects.get_view)




