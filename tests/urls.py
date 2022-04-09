from django.urls import include
from django.urls import path

from django_user_api_key.rest_framework.urls import router

urlpatterns = [
    path("api/", include(router.urls)),
]
