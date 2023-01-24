# from djoser.serializers import UserSerializer
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

# from recipes.models import Subscribe
from recipes.models import Ingredient, Tag
from users.models import User

ERR_MSG = 'Не удается войти в систему с предоставленными учетными данными.'


def unacceptable_username(username):
    if username.lower() == settings.UNACCEPTABLE_USERNAME:
        raise serializers.ValidationError(
            f"The name {settings.UNACCEPTABLE_USERNAME} is not allowed."
        )


class UserListSerializer(
        # GetIsSubscribedMixin,
        serializers.ModelSerializer):
    # is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed'
        )


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',)

    # def validate_password(self, password):
    #     validators.validate_password(password)
    #     return password


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class GetTokenSerializer(serializers.Serializer):
    """Serializer for requests to auth/token/ endpoint."""

    email = serializers.CharField(max_length=254)
    password = serializers.CharField(max_length=150)

    # def validate_username(self, value):
    #     unacceptable_username(value)
    #     return value


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        model = Tag


