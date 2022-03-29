import hashlib
import hmac
import uuid
from typing import Tuple

from django.conf import settings
from django.db import models
from django.utils.encoding import force_bytes


class UserApiKeyManager(models.Manager):
    def _get_secret(self):
        try:
            secret = getattr(settings, "USER_API_KEY_SECRET")
        except AttributeError:
            raise ValueError("USER_API_KEY_SECRET must be configured in settings")

        if not secret:
            raise ValueError("USER_API_KEY_SECRET must be configured in settings")

        return secret

    def _hash_value(self, value):
        secret = self._get_secret()

        return hmac.new(
            force_bytes(secret), msg=force_bytes(value), digestmod=hashlib.sha256
        ).hexdigest()

    def create_key(self, user) -> Tuple["UserApiKey", uuid.UUID]:
        key_val = uuid.uuid4()
        hashed_val = self._hash_value(key_val)

        key = UserApiKey(user=user, api_key=hashed_val)
        key.save(using=self._db)

        return key, key_val

    def with_api_key(self, api_key: str):
        return self.filter(api_key=self._hash_value(api_key))


class UserApiKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False
    )
    api_key = models.CharField(max_length=64, db_index=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True)
    last_used_at = models.DateTimeField(null=True)

    objects = UserApiKeyManager()
