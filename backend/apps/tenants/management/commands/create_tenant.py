"""Create a new tenant and primary domain."""

from django.core.management.base import BaseCommand

from apps.tenants.models import Domain, Restaurant


class Command(BaseCommand):
    help = "Create a tenant restaurant and its primary domain."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--domain", default="")

    def handle(self, *args, **options):
        name = options["name"]
        schema = options["schema"]
        domain = options["domain"]

        restaurant = Restaurant.objects.create(schema_name=schema, name=name)
        if domain:
            Domain.objects.create(domain=domain, tenant=restaurant, is_primary=True)
        self.stdout.write(f"Created tenant schema={schema}")
        self.stdout.write(f"Tenant API prefix: /restaurants/{schema}/")
