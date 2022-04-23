from rest_framework import routers

from django_user_api_key.rest_framework.views import UserApiKeyViewSet

router = routers.SimpleRouter()

router.register(r"apiKeys", UserApiKeyViewSet)

urlpatterns = router.urls
