from rest_framework import routers

from django_pat.rest_framework.views import PersonalAccessTokenViewSet

router = routers.SimpleRouter()

router.register(r"personalAccessTokens", PersonalAccessTokenViewSet)

urlpatterns = router.urls
