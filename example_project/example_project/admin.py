from django.contrib import admin

from django_pat.admin import PersonalAccessTokenAdmin as BasePersonalAccessTokenAdmin
from django_pat.models import PersonalAccessToken
from django_pat_dj_permissions.models import TokenDjangoPermission
from django_pat_permissions.models import PatPermission


class PermissionsInline(admin.TabularInline):
    model = PatPermission


class DjangoPermissionsInline(admin.TabularInline):
    model = TokenDjangoPermission


class PersonalAccessTokenAdmin(BasePersonalAccessTokenAdmin):
    inlines = [
        PermissionsInline,
        DjangoPermissionsInline,
    ]


admin.site.unregister(PersonalAccessToken)
admin.site.register(PersonalAccessToken, PersonalAccessTokenAdmin)
