from django.core.management.base import BaseCommand
from luckyshot_main_app.models import Match

class Command(BaseCommand):
    help = "Deletes all match records from the database"

    def handle(self, *args, **kwargs):
        count, _ = Match.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} match records"))
