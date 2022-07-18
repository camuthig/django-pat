from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from django_pat.middleware import PatAuthenticationMiddleware
from django_pat.models import PersonalAccessToken

User = get_user_model()


class TestPatAuthenticationMiddleware(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_it_parses_default_header(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")

        def handle(request):
            self.assertTrue(request.user.is_authenticated)
            self.assertEqual(user, request.user)

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Access-Token {token_val}")
        m(req)

    @override_settings(PAT_CUSTOM_HEADER="X-Custom-Key")
    def test_it_supports_a_custom_header(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")

        def handle(request):
            self.assertEqual(user, request.user)

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_X_CUSTOM_KEY=f"Access-Token {token_val}")
        m(req)

    @override_settings(PAT_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_supports_a_custom_prefix(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")

        def handle(request):
            self.assertEqual(user, request.user)

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {token_val}")
        m(req)

    @override_settings(PAT_USES_SHARED_HEADER=True)
    def test_it_supports_a_shared_header(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")

        def handle(request):
            self.assertFalse(hasattr(request, "user"))

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Other-Type {token_val}")
        m(req)

    def test_it_sets_last_used_at(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")
        last_used_at = timezone.now() - timedelta(days=1)
        token.last_used_at = last_used_at
        token.save()

        def handle(request):
            token.refresh_from_db()
            self.assertEqual(last_used_at, token.last_used_at)

            # Access the request's user to evaluate the lazy object
            self.assertEqual(user, request.user)

            token.refresh_from_db()
            self.assertGreater(token.last_used_at, timezone.now() - timedelta(minutes=1))

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Access-Token {token_val}")
        m(req)

    def test_it_does_not_use_revoked_tokens(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, token_val = PersonalAccessToken.objects.create_token(user, "name")
        token.revoked_at = timezone.now()
        token.save()

        def handle(request):
            self.assertFalse(request.user.is_authenticated)

        m = PatAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Access-Token {token_val}")
        m(req)
