"""Provision a new tenant in one atomic operation."""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context

from apps.memberships.models import StaffMembership
from apps.tenants.models import Domain, Restaurant

User = get_user_model()


class Command(BaseCommand):
    help = "Provision a new tenant: schema + domain + admin user + manager membership."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--admin-email", required=True)
        parser.add_argument("--admin-password", required=True)

    def handle(self, *args, **options):
        name = options["name"]
        schema = options["schema"]
        email = options["admin_email"]
        password = options["admin_password"]

        with transaction.atomic():
            restaurant = Restaurant.objects.create(schema_name=schema, name=name)
            Domain.objects.create(domain=schema, tenant=restaurant, is_primary=True)

        call_command("migrate_schemas", schema_name=schema, interactive=False, verbosity=0)

        with transaction.atomic():
            user = User.objects.create_user(username=email, email=email, password=password)
            with schema_context(schema):
                StaffMembership.objects.create(
                    user=user,
                    role=StaffMembership.ROLE_MANAGER,
                    is_active=True,
                )

        self.stdout.write(f"Tenant API prefix: /restaurants/{schema}/")
        self.stdout.write(f"Login: /auth/login/ (email: {email})")
