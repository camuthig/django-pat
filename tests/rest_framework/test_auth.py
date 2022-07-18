from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.exceptions import AuthenticationFailed

from django_pat.models import PersonalAccessToken
from django_pat.rest_framework.auth import PatAuthentication

User = get_user_model()


class TestPatAuthentication(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        self.token, self.token_val = PersonalAccessToken.objects.create_token(self.user, "name")

    def test_it_authenticates_an_token(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Access-Token {self.token_val}")
        obj = PatAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.token, found_token)

    def test_it_fails_when_matching_token_not_found(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION="Access-Token not-a-token")
        obj = PatAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_returns_none_if_header_not_present(self):
        req = self.request_factory.get("path")
        obj = PatAuthentication()
        res = obj.authenticate(req)
        self.assertIsNone(res)

    @override_settings(PAT_CUSTOM_HEADER="X-Custom-Header")
    def test_it_uses_custom_header(self):
        req = self.request_factory.get("path", HTTP_X_CUSTOM_HEADER=f"Access-Token {self.token_val}")
        obj = PatAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.token, found_token)

    @override_settings(PAT_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_uses_custom_prefix(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {self.token_val}")
        obj = PatAuthentication()
        found_user, found_token = obj.authenticate(req)

        self.assertEqual(self.user, found_user)
        self.assertEqual(self.token, found_token)

    @override_settings(PAT_USES_SHARED_HEADER=True)
    def test_it_supports_a_shared_header(self):
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {self.token_val}")
        obj = PatAuthentication()
        res = obj.authenticate(req)

        self.assertIsNone(res)

    def test_it_checks_active_users(self):
        self.user.is_active = False
        self.user.save()

        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {self.token_val}")
        obj = PatAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_fails_if_user_is_not_active(self):
        self.user.is_active = False
        self.user.save()

        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Access-Token {self.token_val}")
        obj = PatAuthentication()
        self.assertRaises(AuthenticationFailed, obj.authenticate, req)

    def test_it_returns_configured_keyword_for_authenticate_header(self):
        obj = PatAuthentication()
        self.assertEqual("Access-Token", obj.authenticate_header(self.request_factory.get("path")))

    @override_settings(PAT_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_returns_custom_keyword_for_authenticate_header(self):
        obj = PatAuthentication()
        self.assertEqual("Custom-Key", obj.authenticate_header(self.request_factory.get("path")))
