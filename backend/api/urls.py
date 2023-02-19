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
)

app_name = 'api'

router = DefaultRouter()

router.register('users', UsersViewSet)
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
]
