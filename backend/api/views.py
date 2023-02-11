from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import status, views, generics, viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import CustomPagination
from api.permissions import AdminOrAuthorOrReadOnly
from api.serializers import (
    CustomUserSerializer,
    UserCreateSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializerWrite,
    RecipeSerializerRead,
    FollowSerializerWrite,
    FollowSerializerRead,
    FavoriteSerializerWrite,
    ShoppingCartSerializer
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart, RecipeIngredient
)
from users.models import User, Follow


class UsersViewSet(UserViewSet):
    """Пользователи."""

    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'set_password':
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return CustomUserSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response({'Пароль успешно изменен'}, status=status.HTTP_204_NO_CONTENT)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """Генерация токена."""

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(data=token_serializer_class(token).data, status=status.HTTP_201_CREATED
        )


class TokenDestroyView(views.APIView):
    """Удаление токена."""

    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewWrite(APIView):
    """Подписаться/отписаться на/от пользователя."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id
        }
        serializer = FollowSerializerWrite(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Follow.objects.filter(
                user=request.user,
                author=author).exists():
            subscription = get_object_or_404(
                Follow,
                user=request.user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowViewRead(ListAPIView):
    """Возвращает пользователей, на которых подписан текущий пользователь."""

    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializerRead(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Игредиенты."""

    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    search_fileds = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Создать/получить/обновить/удалить рецепт.
    Добавить/удалить рецепт в/из список покупок/избранное.
    """

    permission_classes = (AdminOrAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerWrite
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerRead
        return RecipeSerializerWrite

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @staticmethod
    def post_delete_method(request, pk, serializers, model):
        user = request.user.pk
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {'user': user, 'recipe': pk}
            serializer = serializers(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        result = get_object_or_404(model, user=user, recipe=recipe)
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True, url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated]
            )
    def shopping_cart(self, request, pk):
        return self.post_delete_method(
            request=request, pk=pk,
            serializers=ShoppingCartSerializer,
            model=ShoppingCart
        )

    @action(methods=['post', 'delete'],
            detail=True, url_path='favorite',
            permission_classes=[AdminOrAuthorOrReadOnly]
            )
    def favorite(self, request, pk):
        return self.post_delete_method(
            request=request,
            pk=pk,
            serializers=FavoriteSerializerWrite,
            model=Favorite
        )


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(ingredient_amount=Sum('amount'))
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['ingredient_amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
