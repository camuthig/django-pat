from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView

from django_pat.models import PersonalAccessToken


class CreateTokenForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(required=False)


class CreateTokenView(LoginRequiredMixin, FormView):
    template_name = "personal_access_token/create.html"
    form_class = CreateTokenForm

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        description = form.cleaned_data["description"]

        try:
            token, plaintext = PersonalAccessToken.objects.create_token(self.request.user, name, description)
        except Exception:
            return self.form_invalid(form)

        return self.render_to_response(self.get_context_data(created_token_value=plaintext))


class ListTokensView(LoginRequiredMixin, ListView):
    template_name = "personal_access_token/list.html"
    model = PersonalAccessToken
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    template_name = "personal_access_token/confirm_delete.html"
    model = PersonalAccessToken
    success_url = reverse_lazy("list_tokens")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: PersonalAccessToken = self.get_object()
        success_url = self.get_success_url()

        self.object.revoke()

        return HttpResponseRedirect(success_url)
