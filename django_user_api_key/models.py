import hashlib
import hmac
import uuid
from typing import Tuple

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.encoding import force_bytes


def _get_secret():
    try:
        secret = getattr(settings, "USER_API_KEY_SECRET")
    except AttributeError:
        raise ValueError("USER_API_KEY_SECRET must be configured in settings")

    if not secret:
        raise ValueError("USER_API_KEY_SECRET must be configured in settings")

    return secret


def _hash_value(value):
    secret = _get_secret()

    return hmac.new(force_bytes(secret), msg=force_bytes(value), digestmod=hashlib.sha256).hexdigest()


class UserApiKeyQuerySet(QuerySet):
    def valid(self):
        return self.filter(revoked_at__isnull=True)

    def with_api_key(self, api_key: str):
        return self.filter(api_key=_hash_value(api_key))


class UserApiKeyManager(models.Manager):
    def get_queryset(self):
        return UserApiKeyQuerySet(self.model, using=self._db)

    def valid(self):
        return self.get_queryset().valid()

    def with_api_key(self, api_key: str) -> QuerySet:
        return self.get_queryset().with_api_key(api_key)

    def create_key(self, user, name: str, description: str = None, commit: bool = True) -> Tuple["UserApiKey", uuid.UUID]:
        key_val = uuid.uuid4()
        hashed_val = _hash_value(key_val)

        key = UserApiKey(user=user, api_key=hashed_val, name=name, description=description or "")

        if commit:
            key.save()

        return key, key_val


class UserApiKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    api_key = models.CharField(max_length=64, db_index=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True)
    last_used_at = models.DateTimeField(null=True)

    objects = UserApiKeyManager()

    class Meta:
        unique_together = ["user", "name"]

    def revoke(self):
        self.revoked_at = timezone.now()
