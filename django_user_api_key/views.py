from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView

from django_user_api_key.models import UserApiKey


class CreateKeyForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(required=False)


class CreateKeyView(LoginRequiredMixin, FormView):
    template_name = "api_key/create.html"
    form_class = CreateKeyForm

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        description = form.cleaned_data["description"]

        try:
            key, plaintext = UserApiKey.objects.create_key(self.request.user, name, description)
        except Exception:
            return self.form_invalid(form)

        return self.render_to_response(self.get_context_data(created_key_value=plaintext))


class ListKeysView(LoginRequiredMixin, ListView):
    template_name = "api_key/list.html"
    model = UserApiKey
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class DeleteKeyView(LoginRequiredMixin, DeleteView):
    template_name = "api_key/confirm_delete.html"
    model = UserApiKey
    success_url = reverse_lazy("list_keys")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: UserApiKey = self.get_object()
        success_url = self.get_success_url()

        self.object.revoke()

        return HttpResponseRedirect(success_url)
