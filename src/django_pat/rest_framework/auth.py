from django.utils.translation import gettext
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django_pat.http import ParseException
from django_pat.http import get_keyword
from django_pat.http import parse_header
from django_pat.models import PersonalAccessToken


class PatAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            token_value = parse_header(request)
        except ParseException as e:
            raise AuthenticationFailed(e.msg)

        if token_value is None:
            return None

        token = PersonalAccessToken.objects.first_valid_token(token_value)

        if not token:
            raise AuthenticationFailed(gettext("Invalid token."))

        if not token.user.is_active:
            raise AuthenticationFailed(gettext("User inactive or deleted."))

        token.mark_used()

        return token.user, token

    def authenticate_header(self, request):
        return get_keyword()
