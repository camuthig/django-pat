from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.test import TestCase

from django_pat.admin import PersonalAccessTokenAdmin
from django_pat.admin import PersonalAccessTokenForm
from django_pat.models import PersonalAccessToken

User = get_user_model()


class MockRequest:
    pass


class PersonalAccessTokenFormTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser("testuser", "test@test.com", "random-insecure-text")
        self.request_factory = RequestFactory()

    def test_it_creates_a_new_key(self):
        form = PersonalAccessTokenForm(data={"name": "Test Key", "description": ""})
        form.current_user = self.user

        self.assertTrue(form.is_valid())
        token = form.save(False)

        self.assertIsNotNone(token.plain_text_value)
        self.assertEqual(token.user, self.user)


class PersonalAccessTokenAdminTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser("testuser", "test@test.com", "random-insecure-text")
        self.request = MockRequest()
        self.request.user = self.user
        self.site = AdminSite()
        self.request_factory = RequestFactory()

    def test_it_uses_the_request_user_in_form(self):
        ma = PersonalAccessTokenAdmin(PersonalAccessToken, self.site)
        ma.get_form(self.request)
        ma.current_user = self.user

    def test_it_flashes_the_key_value_on_save(self):
        request = self.request_factory.post("path", {"name": "Test key", "description": ""})
        request.user = self.user
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        ma = PersonalAccessTokenAdmin(PersonalAccessToken, self.site)
        obj, val = PersonalAccessToken.objects.create_token(self.user, "Test Key", "", False)
        obj.plain_text_value = val
        ma.save_model(request, obj, ma.get_form(request), False)

        message = list(messages).pop()
        self.assertEqual(f"Personal access token value {val}", str(message))

    def test_it_revokes_keys(self):
        ma = PersonalAccessTokenAdmin(PersonalAccessToken, self.site)
        obj, plain = PersonalAccessToken.objects.create_token(self.user, "Test", None)
        ma.delete_model(self.request, obj)
        self.assertIsNotNone(obj.revoked_at)

    def test_it_does_not_allow_editing_keys(self):
        ma = PersonalAccessTokenAdmin(PersonalAccessToken, self.site)
        obj, plain = PersonalAccessToken.objects.create_token(self.user, "Test", None, False)
        self.assertFalse(ma.has_change_permission(self.request, obj))

    def test_it_does_not_allow_deleting_already_revoked_keys(self):
        ma = PersonalAccessTokenAdmin(PersonalAccessToken, self.site)
        obj, plain = PersonalAccessToken.objects.create_token(self.user, "Test", None, False)
        obj.revoke(False)
        self.assertFalse(ma.has_delete_permission(self.request, obj))
