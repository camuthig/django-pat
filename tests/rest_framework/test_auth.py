from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.exceptions import AuthenticationFailed

from django_user_api_key.models import UserApiKey
from django_user_api_key.rest_framework.auth import UserApiKeyAuthentication

User = get_user_model()


class TestUserApiKeyAuthentication(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        self.api_key, self.key_val = UserApiKey.objects.create_key(self.user, "name")

    def test_it_authenticates_an_api_key(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {self.key_val}")
        obj = UserApiKeyAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.api_key, found_token)

    def test_it_fails_when_matching_key_not_found(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION="Api-Key not-a-key")
        obj = UserApiKeyAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_returns_none_if_header_not_present(self):
        req = self.request_factory.get("path")
        obj = UserApiKeyAuthentication()
        res = obj.authenticate(req)
        self.assertIsNone(res)

    @override_settings(USER_API_KEY_CUSTOM_HEADER="X-Custom-Header")
    def test_it_uses_custom_header(self):
        req = self.request_factory.get("path", HTTP_X_CUSTOM_HEADER=f"Api-Key {self.key_val}")
        obj = UserApiKeyAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.api_key, found_token)

    @override_settings(USER_API_KEY_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_uses_custom_prefix(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {self.key_val}")
        obj = UserApiKeyAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.api_key, found_token)

    def test_it_checks_active_users(self):
        self.user.is_active = False
        self.user.save()

        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {self.key_val}")
        obj = UserApiKeyAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_fails_if_user_is_not_active(self):
        self.user.is_active = False
        self.user.save()

        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {self.key_val}")
        obj = UserApiKeyAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_returns_configured_keyword_for_authenticate_header(self):
        obj = UserApiKeyAuthentication()
        self.assertEqual('Api-Key', obj.authenticate_header(self.request_factory.get("path")))

    @override_settings(USER_API_KEY_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_returns_custom_keyword_for_authenticate_header(self):
        obj = UserApiKeyAuthentication()
        self.assertEqual('Custom-Key', obj.authenticate_header(self.request_factory.get("path")))
