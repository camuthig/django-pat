from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser

from django_pat.models import PersonalAccessToken


class PersonalAccessTokenForm(forms.ModelForm):
    current_user: AbstractBaseUser

    class Meta:
        model = PersonalAccessToken
        fields = ["name", "description"]

    def save(self, commit=True):
        token, value = PersonalAccessToken.objects.create_token(
            self.current_user,
            self.cleaned_data["name"],
            self.cleaned_data["description"],
            commit=commit,
        )
        token.plain_text_value = value

        return token

    def save_m2m(self):
        pass


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
