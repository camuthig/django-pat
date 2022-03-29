from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from django_user_api_key.models import UserApiKey


class ApiKeyAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._handle(request)

        response = self.get_response(request)

        # OAuth2 middleware also does the below for reasons that may be worth considering.
        # patch_vary_headers(response, ("Authorization",))

        return response

    def _get_header(self):
        return getattr(settings, "USER_API_KEY_CUSTOM_HEADER", "HTTP_AUTHORIZATION")

    def _get_prefix(self):
        return (
            getattr(settings, "USER_API_KEY_CUSTOM_HEADER_PREFIX", "Api-Key").strip()
            + " "
        )

    def _handle(self, request):
        header_val = str(request.META.get(self._get_header()))
        if not header_val:
            return

        if not header_val.startswith(self._get_prefix()):
            return

        if hasattr("user", request) and not request.user.is_anonymous:
            return

        _, key_val = header_val.split(self._get_prefix())

        def get_user(r):
            api_key = (
                UserApiKey.objects.filter(revoked_at__is_null=True)
                .with_api_key(key_val)
                .selected_related("user")
                .first()
            )

            if not api_key:
                return

            api_key.last_used_at = timezone.now()
            api_key.save()

            r._cached_user = api_key.user
            return r._cached_user

        request.user = SimpleLazyObject(lambda: get_user(request))
