from django.contrib import admin

from django_pat.models import PersonalAccessToken
from django_pat_dj_permissions.admin import PersonalAccessTokenAdmin

admin.site.unregister(PersonalAccessToken)
admin.site.register(PersonalAccessToken, PersonalAccessTokenAdmin)
