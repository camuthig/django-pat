from django.db import models

from django_pat.models import PersonalAccessToken


class Permission(models.Model):
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name


class PatPermission(models.Model):
    token = models.ForeignKey(PersonalAccessToken, related_name="pat_permissions", on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
