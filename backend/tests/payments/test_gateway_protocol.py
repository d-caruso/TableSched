"""Tests for payment gateway protocol compatibility."""


def test_stripe_gateway_satisfies_protocol() -> None:
    from apps.payments.gateways.base import PaymentGateway
    from apps.payments.gateways.stripe import StripeGateway

    _ = PaymentGateway
    for method in (
        "create_preauth",
        "capture",
        "cancel_authorization",
        "create_payment_link",
        "refund",
    ):
        assert hasattr(StripeGateway, method)

