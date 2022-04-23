from django.urls import path

from django_user_api_key.views import CreateKeyView
from django_user_api_key.views import DeleteKeyView
from django_user_api_key.views import ListKeysView

urlpatterns = [
    path("api-keys/new/", CreateKeyView.as_view(), name="create_key"),
    path("api-keys/<int:pk>/delete/", DeleteKeyView.as_view(), name="delete_key"),
    path("api-keys/", ListKeysView.as_view(), name="list_keys"),
]
