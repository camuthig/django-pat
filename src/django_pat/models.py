import hashlib
import hmac
import uuid
from typing import Optional
from typing import Tuple

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.encoding import force_bytes


def _get_secret():
    try:
        secret = getattr(settings, "PAT_SECRET")
    except AttributeError:
        raise ValueError("PAT_SECRET must be configured in settings")

    if not secret:
        raise ValueError("PAT_SECRET must be configured in settings")

    return secret


def _hash_value(value):
    secret = _get_secret()

    return hmac.new(force_bytes(secret), msg=force_bytes(value), digestmod=hashlib.sha256).hexdigest()


class PersonalAccessTokenQuerySet(QuerySet):
    def valid(self):
        return self.filter(revoked_at__isnull=True)

    def with_value(self, value: str):
        return self.filter(hashed_value=_hash_value(value))

    def with_valid_value(self, value: str):
        return self.valid().with_value(value)

    def first_valid_token(self, value: str) -> Optional["PersonalAccessToken"]:
        return self.with_valid_value(value).first()


class PersonalAccessTokenManager(models.Manager):
    def get_queryset(self):
        return PersonalAccessTokenQuerySet(self.model, using=self._db)

    def valid(self):
        return self.get_queryset().valid()

    def with_value(self, value: str):
        return self.get_queryset().with_value(value)

    def first_valid_token(self, value: str) -> Optional["PersonalAccessToken"]:
        return self.get_queryset().with_valid_value(value).first()

    def create_token(
        self,
        user,
        name: str,
        description: Optional[str] = None,
        commit: bool = True,
    ) -> Tuple["PersonalAccessToken", uuid.UUID]:
        token_val = uuid.uuid4()
        hashed_val = _hash_value(token_val)

        token = PersonalAccessToken(user=user, hashed_value=hashed_val, name=name, description=description or "")

        if commit:
            token.save()

        return token, token_val


class PersonalAccessToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    hashed_value = models.CharField(max_length=64, db_index=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True)
    last_used_at = models.DateTimeField(null=True)

    objects = PersonalAccessTokenManager()

    class Meta:
        unique_together = ["user", "name"]

    def revoke(self, commit=True):
        self.revoked_at = timezone.now()
        if commit:
            self.save()

    def mark_used(self, commit=True):
        self.last_used_at = timezone.now()
        if commit:
            self.save()

    def __str__(self):
        return self.name
