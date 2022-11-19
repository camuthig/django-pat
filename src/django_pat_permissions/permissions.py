from django.db.models import QuerySet

from django_pat.permissions import Backend
from django_pat_permissions.models import Permission


class PatPermissionBackend(Backend):
    def _get_permissions(self, token) -> QuerySet["Permission"]:
        # Unashamedly based on the logic used by the Django ModelBackend
        perm_cache_name = "_perm_cache"
        if not hasattr(token, "_perm_cache"):
            if token.user.is_superuser:
                perms: QuerySet = Permission.objects.all()
            else:
                perms = token.pat_permissions.all()
            perms = perms.values_list("name").order_by()
            setattr(token, perm_cache_name, {f"{name}" for name in perms})

        return getattr(token, perm_cache_name)

    def has_any_permission(self, token, *permissions: str):
        return bool(set(permissions).intersection(self._get_permissions(token)))
