from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import RequestFactory
from django.test import TestCase

from django_pat import permissions
from django_pat.models import PersonalAccessToken
from django_pat.rest_framework.permissions import BasePatPermission
from django_pat.rest_framework.permissions import PatPermission
from tests.permissions import MockBackend

User = get_user_model()


class TestBasePermission(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.mock_backend = MockBackend()
        permissions.manager().boot()
        permissions.manager()._backends["default"] = self.mock_backend

    def tearDown(self):
        permissions.manager().clear_cache()

    def test_permission_class(self):
        class SimplePermission(BasePatPermission):
            permission = "test.stuff"

        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, _ = PersonalAccessToken.objects.create_token(user, "name")
        request = HttpRequest()
        request.auth = token

        self.assertFalse(SimplePermission().has_permission(request, None))

        self.mock_backend.add_permission(token, "test.stuff")

        self.assertTrue(SimplePermission().has_permission(request, None))

    def test_dynamic_permission_class(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, _ = PersonalAccessToken.objects.create_token(user, "name")
        request = HttpRequest()
        request.auth = token

        permission_class = PatPermission("test.stuff")

        self.assertFalse(permission_class().has_permission(request, None))

        self.mock_backend.add_permission(token, "test.stuff")

        self.assertTrue(permission_class().has_permission(request, None))
