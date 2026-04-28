"""Tests for customer model and service behavior."""

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from django.db import connection

from apps.customers.models import Customer
from apps.customers.services import upsert_customer


@contextmanager
def customer_table() -> Iterator[None]:
    table_name = Customer._meta.db_table
    table_exists = table_name in connection.introspection.table_names()
    if not table_exists:
        with connection.schema_editor() as editor:
            editor.create_model(Customer)
    yield


@pytest.mark.django_db
def test_upsert_creates_new_customer():
    with customer_table():
        customer = upsert_customer(
            phone="+39123",
            email="a@b.com",
            name="Mario",
            locale="it",
        )
        assert customer.phone == "+39123"
        assert customer.name == "Mario"
        assert customer.email == "a@b.com"
        assert customer.locale == "it"


@pytest.mark.django_db
def test_upsert_dedupes_by_phone():
    with customer_table():
        customer_1 = upsert_customer(
            phone="+39123",
            email="a@b.com",
            name="Mario",
            locale="it",
        )
        customer_2 = upsert_customer(
            phone="+39123",
            email="new@b.com",
            name="Mario",
            locale="it",
        )

        assert customer_1.id == customer_2.id
        customer_1.refresh_from_db()
        assert customer_1.email == "new@b.com"


@pytest.mark.django_db
def test_different_phones_are_different_customers():
    with customer_table():
        customer_1 = upsert_customer(
            phone="+39111",
            email="",
            name="A",
            locale="en",
        )
        customer_2 = upsert_customer(
            phone="+39222",
            email="",
            name="B",
            locale="en",
        )

        assert customer_1.id != customer_2.id
