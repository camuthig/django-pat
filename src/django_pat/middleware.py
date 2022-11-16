from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from django_pat.http import parse_header
from django_pat.models import PersonalAccessToken


class PatAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.handle(request)

        response = self.get_response(request)

        return response

    def handle(self, request: HttpRequest):
        token_value = parse_header(request)

        if token_value is None:
            return

        # TODO Explore a better way to handle typing here.
        request.user = SimpleLazyObject(lambda: self.get_user(request, token_value))  # type: ignore

    def get_user(self, request: HttpRequest, token_value: str):
        # See: https://github.com/typeddjango/django-stubs/issues/728
        token = PersonalAccessToken.objects.select_related("user").first_valid_token(token_value)  # type: ignore

        if not token:
            return AnonymousUser()

        if not token.user.is_active:
            return AnonymousUser()

        token.mark_used()

        # TODO Explore better typing and if _cached_user is worthwhile
        request._cached_user = token.user  # type: ignore
        return request._cached_user  # type: ignore
