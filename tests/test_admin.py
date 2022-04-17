from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.test import TestCase

from django_user_api_key.admin import UserApiKeyAdmin
from django_user_api_key.admin import UserApiKeyForm
from django_user_api_key.models import UserApiKey

User = get_user_model()


class MockRequest:
    pass


class UserApiKeyFormTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser("testuser", "test@test.com", "random-insecure-text")
        self.request_factory = RequestFactory()

    def test_it_creates_a_new_key(self):
        form = UserApiKeyForm(data={"name": "Test Key", "description": ""})
        form.current_user = self.user

        self.assertTrue(form.is_valid())
        api_key = form.save(False)

        self.assertIsNotNone(api_key.plain_text_key)
        self.assertEqual(api_key.user, self.user)


class UserApiKeyAdminTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser("testuser", "test@test.com", "random-insecure-text")
        self.request = MockRequest()
        self.request.user = self.user
        self.site = AdminSite()
        self.request_factory = RequestFactory()

    def test_it_uses_the_request_user_in_form(self):
        ma = UserApiKeyAdmin(UserApiKey, self.site)
        ma.get_form(self.request)
        ma.current_user = self.user

    def test_it_flashes_the_key_value_on_save(self):
        request = self.request_factory.post("path", {"name": "Test key", "description": ""})
        request.user = self.user
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        ma = UserApiKeyAdmin(UserApiKey, self.site)
        obj, val = UserApiKey.objects.create_key(self.user, "Test Key", "", False)
        obj.plain_text_key = val
        ma.save_model(request, obj, ma.get_form(request), False)

        message = list(messages).pop()
        self.assertEqual(f"API Key value {val}", str(message))

    def test_it_revokes_keys(self):
        ma = UserApiKeyAdmin(UserApiKey, self.site)
        obj, plain = UserApiKey.objects.create_key(self.user, "Test", None)
        ma.delete_model(self.request, obj)
        self.assertIsNotNone(obj.revoked_at)

    def test_it_does_not_allow_editing_keys(self):
        ma = UserApiKeyAdmin(UserApiKey, self.site)
        obj, plain = UserApiKey.objects.create_key(self.user, "Test", None, False)
        self.assertFalse(ma.has_change_permission(self.request, obj))

    def test_it_does_not_allow_deleting_already_revoked_keys(self):
        ma = UserApiKeyAdmin(UserApiKey, self.site)
        obj, plain = UserApiKey.objects.create_key(self.user, "Test", None, False)
        obj.revoke(False)
        self.assertFalse(ma.has_delete_permission(self.request, obj))
