"""Membership middleware."""


class MembershipMiddleware:
    """Placeholder middleware for tenant membership resolution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
