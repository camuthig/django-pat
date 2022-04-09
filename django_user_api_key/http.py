from django.conf import settings
from django.utils.translation import gettext


class ParseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def get_header():
    return getattr(settings, "USER_API_KEY_CUSTOM_HEADER", "Authorization")


def get_keyword():
    return getattr(settings, "USER_API_KEY_CUSTOM_HEADER_PREFIX", "Api-Key").strip()


def parse_header(request):
    header = get_header()

    if header not in request.headers:
        return

    header_val = str(request.headers.get(get_header()))
    if not header_val:
        raise ParseException(gettext("Invalid header"))

    if not header_val.startswith(get_keyword() + " "):
        raise ParseException(gettext("Invalid header"))

    _, key_val = header_val.split(get_keyword() + " ")

    return key_val
