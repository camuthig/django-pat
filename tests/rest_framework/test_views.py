from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from django_user_api_key.models import UserApiKey

User = get_user_model()


class TestUserApiKeyViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        self.client.force_login(self.user)

    def test_creates_a_new_key_for_the_current_user(self):
        url = reverse("userapikey-list")
        response = self.client.post(url, data={"name": "New Key 1"})

        j = response.json()
        self.assertEqual(self.user.id, j["user"])
        self.assertIn("plain_text", j)
        self.assertIsNotNone(j["plain_text"])
        self.assertTrue(len(j["plain_text"]) > 0)

    def test_post_validates_unique_names(self):
        UserApiKey.objects.create_key(self.user, "Existing Key")
        url = reverse("userapikey-list")
        response = self.client.post(url, data={"name": "Existing Key"})

        self.assertEqual(400, response.status_code)

    def test_list_returns_current_users_keys(self):
        expected_key, _ = UserApiKey.objects.create_key(self.user, "Existing Key")
        other_user = User.objects.create_user("otheruser", "test@test.com", "random-insecure-text")
        other_key, _ = UserApiKey.objects.create_key(other_user, "Other Key")

        url = reverse("userapikey-list")
        response = self.client.get(url)

        j = response.json()
        self.assertEqual(1, len(j))
        self.assertEqual(expected_key.id, j[0]["id"])

    def test_delete_revokes_users_token(self):
        api_key, _ = UserApiKey.objects.create_key(self.user, "Existing Key")
        url = reverse("userapikey-detail", kwargs={"pk": api_key.id})

        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        api_key.refresh_from_db()
        self.assertIsNotNone(api_key.revoked_at)
