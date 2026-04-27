"""Tests for error code responses."""

from apps.common.codes import ErrorCode
from apps.common.errors import DomainError


def test_domain_error_shape():
    exc = DomainError(ErrorCode.VALIDATION_FAILED, {"field": "starts_at"})
    assert exc.detail == {"error_code": "validation_failed", "params": {"field": "starts_at"}}


def test_domain_error_no_localized_string():
    exc = DomainError("booking_cutoff_passed")
    assert isinstance(exc.detail["error_code"], str)
    assert " " not in exc.detail["error_code"]
