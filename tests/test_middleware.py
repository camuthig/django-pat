from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from django_user_api_key.middleware import ApiKeyAuthenticationMiddleware
from django_user_api_key.models import UserApiKey

User = get_user_model()


class TestApiKeyAuthenticationMiddleware(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_it_parses_default_key(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)

        def handle(request):
            self.assertTrue(request.user.is_authenticated)
            self.assertEqual(user, request.user)

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {key_val}")
        m(req)

    def test_it_defers_to_existing_auth_if_set(self):
        already_authenticated_user = User.objects.create_user("user1", "user1@test.com", "random-insecure-text")
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)

        def handle(request):
            self.assertEqual(already_authenticated_user, request.user)

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {key_val}")
        req.user = SimpleLazyObject(lambda: already_authenticated_user)
        m(req)

    @override_settings(USER_API_KEY_CUSTOM_HEADER="X-Custom-Key")
    def test_it_supports_a_custom_header(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)

        def handle(request):
            self.assertEqual(user, request.user)

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_X_CUSTOM_KEY=f"Api-Key {key_val}")
        m(req)

    @override_settings(USER_API_KEY_CUSTOM_HEADER_PREFIX="Custom-Key")
    def test_it_supports_a_custom_prefix(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)

        def handle(request):
            self.assertEqual(user, request.user)

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Custom-Key {key_val}")
        m(req)

    def test_it_sets_last_used_at(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)
        last_used_at = timezone.now() - timedelta(days=1)
        api_key.last_used_at = last_used_at
        api_key.save()

        def handle(request):
            api_key.refresh_from_db()
            self.assertEqual(last_used_at, api_key.last_used_at)

            # Access the request's user to evaluate the lazy object
            self.assertEqual(user, request.user)

            api_key.refresh_from_db()
            self.assertGreater(api_key.last_used_at, timezone.now() - timedelta(minutes=1))

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {key_val}")
        m(req)

    def test_it_does_not_use_revoked_keys(self):
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        api_key, key_val = UserApiKey.objects.create_key(user)
        api_key.revoked_at = timezone.now()
        api_key.save()

        def handle(request):
            self.assertFalse(request.user.is_authenticated)

        m = ApiKeyAuthenticationMiddleware(handle)
        req = self.request_factory.get("path", HTTP_AUTHORIZATION=f"Api-Key {key_val}")
        m(req)
