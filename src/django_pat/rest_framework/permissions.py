from typing import Type

from rest_framework.permissions import BasePermission

from django_pat.models import PersonalAccessToken


class BasePatPermission(BasePermission):
    permission: str
    using: str | None = None

    def has_permission(self, request, view):
        if not hasattr(request, "auth"):
            return False

        if not isinstance(request.auth, PersonalAccessToken):
            return False

        return request.auth.has_permission(self.permission, self.using)


def PatPermission(permission: str, using: str = None) -> Type[BasePatPermission]:  # noqa fmt: skip
    """
    A function to generate dynamic permissions while matching the style of Rest Framework permission classes.

    This can be used in views as `PatPermission("some.permission")`. This would be the equivalent of a class defined as

    ```python
    class SomePermission(BasePatPermission):
        permission = "some.permission"
    ```
    """
    _permission = permission
    _using = using

    class InnerPatPermission(BasePatPermission):
        permission = _permission
        using = _using

    return InnerPatPermission
