import pytest


@pytest.fixture(autouse=True)
def _public_tenant(public_tenant):
    pass
