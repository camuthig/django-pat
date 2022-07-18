from typing import Union

from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from django_pat.models import PersonalAccessToken

UserFieldType = Union[serializers.PrimaryKeyRelatedField, AbstractUser]


class CreatePersonalAccessTokenSerializer(serializers.ModelSerializer):
    user: UserFieldType = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    plain_text = serializers.CharField(read_only=True)
    revoked_at = serializers.DateTimeField(read_only=True)
    last_used_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PersonalAccessToken
        fields = ["id", "name", "description", "user", "plain_text", "revoked_at", "last_used_at"]
        readonly = ["id", "user", "plain_text", "revoked_at", "last_used_at"]


class PersonalAccessTokenViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    queryset = PersonalAccessToken.objects.all()
    serializer_class = CreatePersonalAccessTokenSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer: CreatePersonalAccessTokenSerializer):  # type: ignore[override]
        token, plain_text = PersonalAccessToken.objects.create_token(  # type: ignore
            self.request.user,
            serializer.validated_data.get("name"),
            serializer.validated_data.get("description", ""),
        )

        # TODO Explore a better way to handle typing here.
        token.plain_text = plain_text  # type: ignore

        serializer.instance = token  # type: ignore

    def perform_destroy(self, instance: PersonalAccessToken):
        instance.revoke()
