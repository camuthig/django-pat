from django.utils.translation import gettext
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django_user_api_key.http import ParseException
from django_user_api_key.http import get_keyword
from django_user_api_key.http import parse_header
from django_user_api_key.models import UserApiKey


class UserApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            key_value = parse_header(request)
        except ParseException as e:
            raise AuthenticationFailed(e.msg)

        if key_value is None:
            return None

        api_key = UserApiKey.objects.first_valid_key(key_value)

        if not api_key:
            raise AuthenticationFailed(gettext("Invalid token."))

        if not api_key.user.is_active:
            raise AuthenticationFailed(gettext("User inactive or deleted."))

        api_key.mark_used()

        return api_key.user, api_key

    def authenticate_header(self, request):
        return get_keyword()
