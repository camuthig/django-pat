import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from django_pat.models import PersonalAccessToken
from django_pat.models import PersonalAccessTokenManager

User = get_user_model()


class TestPersonalAccessTokenManager(TestCase):
    def test_it_creates_an_token(self):
        manager = PersonalAccessTokenManager()
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token, _ = manager.create_token(user, "name")
        self.assertIsNotNone(token)
        self.assertEqual(user, token.user)

    @override_settings()
    def test_it_fails_to_create_user_without_secret_set(self):
        del settings.PAT_SECRET
        manager = PersonalAccessTokenManager()
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        with pytest.raises(ValueError):
            token, _ = manager.create_token(user, "name")

    @override_settings(PAT_SECRET=None)
    def test_it_fails_to_create_user_without_valid_secret_set(self):
        manager = PersonalAccessTokenManager()
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        with pytest.raises(ValueError):
            token, _ = manager.create_token(user, "name")

    def test_it_gets_a_record_by_token_value(self):
        manager = PersonalAccessTokenManager()
        user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        token1, token_val1 = manager.create_token(user, "name")
        token2, token_val2 = manager.create_token(user, "other")

        self.assertEqual(PersonalAccessToken.objects.with_value(token_val1).first(), token1)
        self.assertEqual(PersonalAccessToken.objects.with_value(token_val2).first(), token2)
