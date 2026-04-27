"""Tests for shared common models."""

import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import pytest
from django.db import connection, models

from apps.common.models import TimeStampedModel


class SampleModel(TimeStampedModel):
    name: models.CharField[str, str] = models.CharField(max_length=32, default="sample")

    class Meta:
        app_label = "tests"
        db_table = "tests_sample_timestamped_model"
        managed = False


@contextmanager
def sample_model_table() -> Iterator[None]:
    with connection.schema_editor() as editor:
        editor.create_model(SampleModel)
    try:
        yield
    finally:
        with connection.schema_editor() as editor:
            editor.delete_model(SampleModel)


@pytest.mark.django_db(transaction=True)
def test_timestamped_model_uuid_pk():
    instance = SampleModel()
    assert isinstance(instance.id, uuid.UUID)


@pytest.mark.django_db(transaction=True)
def test_timestamped_model_created_at():
    with sample_model_table():
        instance = SampleModel.objects.create()
        assert isinstance(instance.created_at, datetime)
        assert isinstance(instance.updated_at, datetime)
