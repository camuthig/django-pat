from django.contrib import admin

from django_pat.admin import PersonalAccessTokenAdmin as BasePersonalAccessTokenAdmin
from django_pat.models import PersonalAccessToken
from django_pat_permissions.models import PatPermission
from django_pat_permissions.models import Permission


class PermissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Permission, PermissionAdmin)


class PermissionsInline(admin.TabularInline):
    model = PatPermission


class PersonalAccessTokenAdmin(BasePersonalAccessTokenAdmin):
    inlines = [
        PermissionsInline,
    ]


admin.site.unregister(PersonalAccessToken)
admin.site.register(PersonalAccessToken, PersonalAccessTokenAdmin)
