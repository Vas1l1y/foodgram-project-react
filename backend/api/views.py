"""URLs request handlers of the 'api' application."""
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.db.models import Exists, OuterRef, Value
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status, views, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import UserListSerializer, UserCreateSerializer, IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag
from users.models import User


class UsersViewSet(UserViewSet):
    """Пользователи."""

    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.follower.filter(
                    author=OuterRef('id'))
            )).prefetch_related(
                'follower', 'following'
        ) if self.request.user.is_authenticated else User.objects.annotate(
            is_subscribed=Value(False))

    def get_serializer_class(self):
        if self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    # @action(
    #     detail=False,
    #     permission_classes=(IsAuthenticated,))
    # def subscriptions(self, request):
    #     """Получить на кого пользователь подписан."""
    #
    #     user = request.user
    #     queryset = Subscribe.objects.filter(user=user)
    #     pages = self.paginate_queryset(queryset)
    #     serializer = SubscribeSerializer(
    #         pages, many=True,
    #         context={'request': request})
    #     return self.get_paginated_response(serializer.data)
    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response({'Пароль успешно изменен'}, status=status.HTTP_204_NO_CONTENT)


# class TokenSerializer(serializers.ModelSerializer):
#     auth_token = serializers.CharField(source="key")
#
#     class Meta:
#         model = settings.TOKEN_MODEL
#         fields = ("auth_token",)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )


class TokenDestroyView(views.APIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """

    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
