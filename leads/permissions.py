from rest_framework import permissions
from django.conf import settings


class IsAIBotOrAdmin(permissions.BasePermission):
    """
    Allows access to AI Bot via API Key or to Admin users.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True

        api_key = request.headers.get("X-Api-Key")
        expected_key = getattr(settings, "LEADS_API_KEY", None)

        if api_key and expected_key and api_key == expected_key:
            return True

        return False
