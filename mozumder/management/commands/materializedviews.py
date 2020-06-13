from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.apps import AppConfig
from ...db.materializedviews.materializedviews import MaterializedViewModel
class Command(BaseCommand):

    help = 'Manage database materialized views.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            '-c','--clear',
            action='store_true',
            dest='clear_views',
            default=False,
            help='Clear Materialized Views',
            )
        parser.add_argument(
            '-l','--load',
            action='store_true',
            dest='load_views',
            default=False,
            help='Load Materialized Views',
            )
        parser.add_argument(
            '-r','--refresh',
            action='store_true',
            dest='refresh_views',
            default=False,
            help='Refresh (clear then reload) Materialized Views',
            )
        parser.add_argument(
            'appname',
            action='store',
            nargs='?',
            default=None,
            help='App containing the models you want to update',
            )
        parser.add_argument(
            'modelname',
            action='store',
            nargs='*',
            default=None,
            help='Specific materialized view table to update (or all in app none selected)',
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
        if options['clear_views']:
            for model in models:
                if issubclass(model,MaterializedViewModel):
                    print(f'Clearing materialized views for model {model.__name__}'
                        f' (database table {model._meta.db_table})' )
                    model.objects.clear()
        if options['load_views']:
            for model in models:
                if issubclass(model,MaterializedViewModel):
                    print(f'Loading materialized views for model {model.__name__}'
                        f' (database table {model._meta.db_table})' )
                    model.objects.load()
        if options['refresh_views']:
            for model in models:
                if issubclass(model,MaterializedViewModel):
                    print(f'Refreshing materialized views for model {model.__name__}'
                        f' (database table {model._meta.db_table})' )
                    model.objects.refresh()



