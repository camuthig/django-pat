from rest_framework.permissions import BasePermission

from django_pat.models import PersonalAccessToken


class PatPermission(BasePermission):
    def __init__(self, permission: str, using: str = None):
        self.permission = permission
        self.using = using

    def has_permission(self, request, view):
        if not hasattr(request, "auth"):
            return False

        if not isinstance(request.auth, PersonalAccessToken):
            return False

        return request.auth.has_permission(self.permission, self.using)

    def __call__(self):
        # WIP Should this return a new instance instead?
        return self
