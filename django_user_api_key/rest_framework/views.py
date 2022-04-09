from typing import Union

from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from django_user_api_key.models import UserApiKey

UserFieldType = Union[serializers.PrimaryKeyRelatedField, AbstractUser]


class CreateUserApiKeySerializer(serializers.ModelSerializer):
    user: UserFieldType = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    plain_text = serializers.CharField(read_only=True)
    revoked_at = serializers.DateTimeField(read_only=True)
    last_used_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserApiKey
        fields = ["id", "name", "description", "user", "plain_text", "revoked_at", "last_used_at"]
        readonly = ["id", "user", "plain_text", "revoked_at", "last_used_at"]


class UserApiKeyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    queryset = UserApiKey.objects.all()
    serializer_class = CreateUserApiKeySerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer: CreateUserApiKeySerializer):  # type: ignore[override]
        api_key, plain_text = UserApiKey.objects.create_key(
            self.request.user,
            serializer.validated_data.get("name"),
            serializer.validated_data.get("description", ""),
        )

        # TODO Explore a better way to handle typing here.
        api_key.plain_text = plain_text  # type: ignore

        serializer.instance = api_key

    def perform_destroy(self, instance: UserApiKey):
        instance.revoke()
