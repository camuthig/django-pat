from collections import defaultdict

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import RequestFactory
from django.test import TestCase

from django_pat.models import PersonalAccessToken
from django_pat.permissions import Backend
from django_pat.permissions import get_backend
from django_pat.rest_framework.permissions import BasePatPermission

User = get_user_model()


class MockBackend(Backend):
    def __init__(self):
        self._permissions = defaultdict(set)

    def add_permission(self, token, permission: str):
        self._permissions[token].add(permission)

    def remove_permission(self, token, permission: str):
        self._permissions[token].remove(permission)

    def has_permission(self, token, permission: str) -> bool:
        return permission in (self._permissions.get(token) or [])


class TestBasePermission(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_permission_class(self):
        mock_backend: MockBackend = get_backend("default")  # type: ignore

        class SimplePermission(BasePatPermission):
            permission = "test.stuff"

        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, _ = PersonalAccessToken.objects.create_token(user, "name")
        request = HttpRequest()
        request.auth = token

        self.assertFalse(SimplePermission().has_permission(request, None))

        mock_backend.add_permission(token, "test.stuff")

        self.assertTrue(SimplePermission().has_permission(request, None))
