from django.urls import path

from django_pat.views import CreateTokenView
from django_pat.views import DeleteTokenView
from django_pat.views import ListTokensView

urlpatterns = [
    path("personal-access-tokens/new/", CreateTokenView.as_view(), name="create_token"),
    path("personal-access-tokens/<int:pk>/delete/", DeleteTokenView.as_view(), name="delete_token"),
    path("personal-access-tokens/", ListTokensView.as_view(), name="list_tokens"),
]
