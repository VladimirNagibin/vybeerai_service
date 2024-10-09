from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class UserTokenCreationSerializer(serializers.Serializer):
    """Сериализатор для получения токена пользователем."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        user = get_object_or_404(User, username=self.data.get('username'))
        if not user.check_password(validated_data.get('password')):
            raise serializers.ValidationError('Неверное имя или пароль')
        return str(AccessToken.for_user(user))
