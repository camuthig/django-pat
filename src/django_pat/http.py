from django.conf import settings
from django.utils.translation import gettext


class ParseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def uses_shared_header() -> bool:
    return getattr(settings, "PAT_USES_SHARED_HEADER", False)


def get_header():
    return getattr(settings, "PAT_CUSTOM_HEADER", "Authorization")


def get_keyword():
    return getattr(settings, "PAT_CUSTOM_HEADER_PREFIX", "Access-Token").strip()


def parse_header(request):
    header = get_header()

    if header not in request.headers:
        return

    header_val = str(request.headers.get(get_header()))
    if not header_val:
        raise ParseException(gettext("Invalid header"))

    starts_with_prefix = header_val.startswith(get_keyword() + " ")
    if not starts_with_prefix and uses_shared_header():
        return

    if not starts_with_prefix:
        raise ParseException(gettext("Invalid authentication type"))

    _, token_val = header_val.split(get_keyword() + " ")

    return token_val
