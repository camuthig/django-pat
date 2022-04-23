from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from django_user_api_key.http import parse_header
from django_user_api_key.models import UserApiKey


class ApiKeyAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.handle(request)

        response = self.get_response(request)

        return response

    def handle(self, request: HttpRequest):
        key_value = parse_header(request)

        if key_value is None:
            return

        # TODO Explore a better way to handle typing here.
        request.user = SimpleLazyObject(lambda: self.get_user(request, key_value))  # type: ignore

    def get_user(self, request: HttpRequest, key_value: str):
        # See: https://github.com/typeddjango/django-stubs/issues/728
        api_key = UserApiKey.objects.select_related("user").first_valid_key(key_value)  # type: ignore

        if not api_key:
            return AnonymousUser()

        api_key.mark_used()

        # TODO Explore better typing and if _cached_user is worthwhile
        request._cached_user = api_key.user  # type: ignore
        return request._cached_user  # type: ignore
