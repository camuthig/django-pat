from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from django_pat.models import PersonalAccessToken

User = get_user_model()


class TestPersonalAccessTokenViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("testuser", "test@test.com", "random-insecure-text")
        self.client.force_login(self.user)

    def test_creates_a_new_token_for_the_current_user(self):
        url = reverse("personalaccesstoken-list")
        response = self.client.post(url, data={"name": "New Token 1"})

        j = response.json()
        self.assertEqual(self.user.id, j["user"])
        self.assertIn("plain_text", j)
        self.assertIsNotNone(j["plain_text"])
        self.assertTrue(len(j["plain_text"]) > 0)

    def test_post_validates_unique_names(self):
        PersonalAccessToken.objects.create_token(self.user, "Existing Token")
        url = reverse("personalaccesstoken-list")
        response = self.client.post(url, data={"name": "Existing Token"})

        self.assertEqual(400, response.status_code)

    def test_list_returns_current_users_tokens(self):
        expected_token, _ = PersonalAccessToken.objects.create_token(self.user, "Existing Token")
        other_user = User.objects.create_user("otheruser", "test@test.com", "random-insecure-text")
        other_token, _ = PersonalAccessToken.objects.create_token(other_user, "Other Token")

        url = reverse("personalaccesstoken-list")
        response = self.client.get(url)

        j = response.json()
        self.assertEqual(1, len(j))
        self.assertEqual(expected_token.id, j[0]["id"])

    def test_delete_revokes_users_token(self):
        token, _ = PersonalAccessToken.objects.create_token(self.user, "Existing Token")
        url = reverse("personalaccesstoken-detail", kwargs={"pk": token.id})

        response = self.client.delete(url)
        self.assertEqual(204, response.status_code)

        token.refresh_from_db()
        self.assertIsNotNone(token.revoked_at)
