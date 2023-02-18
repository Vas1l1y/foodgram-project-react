from django.urls import include, path
from djoser import views
from rest_framework.routers import DefaultRouter

from api.views import (
    UsersViewSet,
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    FollowViewRead,
    FollowViewWrite,
    download_shopping_cart
)

app_name = 'api'

router = DefaultRouter()

router.register('users', UsersViewSet)
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
     path(
          'auth/token/login/',
          views.TokenCreateView.as_view(),
          name="login"
     ),
     path(
          'auth/token/logout/',
          views.TokenDestroyView.as_view(),
          name="logout"
     ),
     path(
          'users/subscriptions/',
          FollowViewRead.as_view(),
          name='subscriptions'
     ),
     path(
          'users/<int:id>/subscribe/',
          FollowViewWrite.as_view(),
          name='subscribe'
     ),
     path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
     ),
     path('', include(router.urls)),
     path('', include('djoser.urls')),
]
