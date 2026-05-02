"""Common middleware."""

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


class CsrfExemptAllauthAppMiddleware:
    """Mark allauth headless app-client requests as CSRF-exempt.

    django-tenants re-resolves the URL conf in process_request, which causes
    the csrf_exempt attribute on allauth's app_view decorator to be lost by
    the time CsrfViewMiddleware.process_view runs.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path.startswith("/_allauth/app/"):
            setattr(request, "_dont_enforce_csrf_checks", True)
        return self.get_response(request)
