"""One-time platform initialisation command."""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.tenants.models import Restaurant


class Command(BaseCommand):
    help = "One-time setup: run shared migrations and create the public tenant row."

    def handle(self, *args, **options):
        call_command("migrate_schemas", "--shared", interactive=False, verbosity=0)
        _, created = Restaurant.objects.get_or_create(
            schema_name="public", defaults={"name": "Public"}
        )
        if created:
            self.stdout.write("Created public tenant row.")
        else:
            self.stdout.write("Public tenant row already exists.")
        self.stdout.write("Platform initialised.")
