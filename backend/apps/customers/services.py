"""Customer domain services."""

from apps.customers.models import Customer


def upsert_customer(*, phone: str, email: str, name: str, locale: str) -> Customer:
    """Create a customer by phone or update mutable fields on existing record."""

    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={"email": email, "name": name, "locale": locale},
    )
    if created:
        return customer

    changed = False
    if email and customer.email != email:
        customer.email = email
        changed = True
    if name and customer.name != name:
        customer.name = name
        changed = True
    if locale and customer.locale != locale:
        customer.locale = locale
        changed = True
    if changed:
        customer.save(update_fields=["email", "name", "locale", "updated_at"])

    return customer
