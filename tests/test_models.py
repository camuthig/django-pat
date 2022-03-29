import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from django_user_api_key.models import UserApiKey
from django_user_api_key.models import UserApiKeyManager

User = get_user_model()


class TestUserApiKeyManager(TestCase):
    def test_it_creates_an_api_key(self):
        manager = UserApiKeyManager()
        user = User.objects.create_user(
            "testuser", "test@test.com", "random-insecure-text"
        )
        api_key, _ = manager.create_key(user)
        self.assertIsNotNone(api_key)
        self.assertEqual(user, api_key.user)

    @override_settings()
    def test_it_fails_to_create_user_without_secret_set(self):
        del settings.USER_API_KEY_SECRET
        manager = UserApiKeyManager()
        user = User.objects.create_user(
            "testuser", "test@test.com", "random-insecure-text"
        )
        with pytest.raises(ValueError):
            api_key, _ = manager.create_key(user)

    @override_settings(USER_API_KEY_SECRET=None)
    def test_it_fails_to_create_user_without_valid_secret_set(self):
        manager = UserApiKeyManager()
        user = User.objects.create_user(
            "testuser", "test@test.com", "random-insecure-text"
        )
        with pytest.raises(ValueError):
            api_key, _ = manager.create_key(user)

    def test_it_gets_a_record_by_key_value(self):
        manager = UserApiKeyManager()
        user = User.objects.create_user(
            "testuser", "test@test.com", "random-insecure-text"
        )
        api_key1, key_val1 = manager.create_key(user)
        api_key2, key_val2 = manager.create_key(user)

        self.assertEqual(UserApiKey.objects.with_api_key(key_val1).first(), api_key1)
        self.assertEqual(UserApiKey.objects.with_api_key(key_val2).first(), api_key2)
