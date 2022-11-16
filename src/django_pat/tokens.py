import hashlib
import hmac
import uuid
from typing import Tuple

from django.conf import settings
from django.utils.encoding import force_bytes


def _get_secret() -> str:
    try:
        secret = getattr(settings, "PAT_SECRET")
    except AttributeError:
        raise ValueError("PAT_SECRET must be configured in settings")

    if not secret:
        raise ValueError("PAT_SECRET must be configured in settings")

    return secret


def _hash_value(value) -> str:
    secret = _get_secret()

    return hmac.new(force_bytes(secret), msg=force_bytes(value), digestmod=hashlib.sha256).hexdigest()


def generate() -> Tuple[str, uuid.UUID]:
    token_val = uuid.uuid4()
    hashed_val = _hash_value(token_val)

    return hashed_val, token_val
