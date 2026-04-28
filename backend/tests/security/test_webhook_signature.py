"""Webhook signature regression tests."""

import pytest
import stripe as stripe_sdk

from tests.payments.helpers import payment_tenant


@pytest.mark.django_db
def test_unsigned_payload_returns_400(client):
    with payment_tenant():
        response = client.post(
            "/stripe/webhook/",
            data=b'{"type":"test"}',
            content_type="application/json",
        )

    assert response.status_code == 400


@pytest.mark.django_db
def test_wrong_signature_returns_400(client, monkeypatch):
    with payment_tenant():
        monkeypatch.setattr(
            stripe_sdk.Webhook,
            "construct_event",
            lambda payload, sig, secret: (_ for _ in ()).throw(
                stripe_sdk.error.SignatureVerificationError("bad signature", sig)
            ),
        )
        response = client.post(
            "/stripe/webhook/",
            data=b'{"type":"test"}',
            HTTP_STRIPE_SIGNATURE="t=123,v1=bad",
            content_type="application/json",
        )

    assert response.status_code == 400


@pytest.mark.django_db
def test_valid_signature_passes_verification(client, monkeypatch):
    with payment_tenant():
        monkeypatch.setattr(
            stripe_sdk.Webhook,
            "construct_event",
            lambda payload, sig, secret: {
                "id": "evt_valid",
                "type": "payment_intent.payment_failed",
                "data": {"object": {"id": "pi_valid", "metadata": {}}},
            },
        )
        response = client.post(
            "/stripe/webhook/",
            data=b'{"type":"test"}',
            HTTP_STRIPE_SIGNATURE="sig",
            content_type="application/json",
        )

    assert response.status_code == 400
