from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser

from django_pat import tokens
from django_pat.models import PersonalAccessToken


class PersonalAccessTokenForm(forms.ModelForm):
    current_user: AbstractBaseUser

    class Meta:
        model = PersonalAccessToken
        fields = ["name", "description"]

    def save(self, commit=True):
        # To ensure m2m and relationships are saved as well, we cannot use the PersonalAccessToken.create_token
        # constructor function. Instead, this code is manually pushing the hashed value and user onto the newly created
        # model.
        self.instance.hashed_value, self.instance.plain_text_value = tokens.generate()
        self.instance.user = self.current_user
        return super().save(commit)


class PersonalAccessTokenAdmin(admin.ModelAdmin):
    form = PersonalAccessTokenForm
    list_display = ["user", "name", "last_used_at", "revoked_at"]
    fields = ["user", "name", "description", "last_used_at", "revoked_at"]
    readonly_fields = ["user", "last_used_at", "revoked_at"]

    def delete_model(self, request, obj: PersonalAccessToken) -> None:
        obj.revoke()

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return obj and not obj.revoked_at

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"Personal access token value {obj.plain_text_value}")


admin.site.register(PersonalAccessToken, PersonalAccessTokenAdmin)
