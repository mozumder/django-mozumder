from django.core.management.base import BaseCommand

from ...models.development import TrackedApp

class Command(BaseCommand):

    help = 'Add a new model to an app.'
    
    def add_arguments(self, parser):

        parser.add_argument(
            '--old',
            action='store_true',
            default=False,
            help='Use original Django app model',
            )
        parser.add_argument(
            'app_name',
            action='store',
            help='App name',
            )
    def handle(self, *args, **options):

        # Create app
        tracked_app, app_created = TrackedApp.objects.get_or_create(name=options['app_name'])
        tracked_app.save()

