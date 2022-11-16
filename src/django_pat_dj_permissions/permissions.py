from django.contrib.auth.models import Permission
from django.db.models import QuerySet

from django_pat.permissions import Backend


class DjangoModelBackend(Backend):
    def _get_permissions(self, token) -> QuerySet["Permission"]:
        # Unashamedly based on the logic used by the Django ModelBackend
        perm_cache_name = "_perm_cache"
        if not hasattr(token, "_perm_cache"):
            if token.user.is_superuser:
                perms: QuerySet = Permission.objects.all()
            else:
                perms = token.django_permissions.all()
            perms = perms.values_list("permission__content_type__app_label", "permission__codename").order_by()
            setattr(token, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})

        return getattr(token, perm_cache_name)

    def has_permission(self, token, permission: str):
        return permission in self._get_permissions(token)
