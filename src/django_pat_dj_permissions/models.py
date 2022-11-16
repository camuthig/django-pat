from django.contrib.auth.models import Permission
from django.db import models

from django_pat.models import PersonalAccessToken


class TokenDjangoPermission(models.Model):
    token = models.ForeignKey(PersonalAccessToken, related_name="django_permissions", on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
