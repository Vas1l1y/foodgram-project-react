from django.urls import include, path
from djoser import views
from rest_framework.routers import DefaultRouter

from api.views import (
     UsersViewSet,
     IngredientViewSet, TagViewSet,
     # get_token
)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet)
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)


urlpatterns = [
     path('', include(router.urls)),
     path('', include('djoser.urls')),
     # path('auth/token/login/', get_token, name="get_token"),
     path('auth/token/login/', views.TokenCreateView.as_view(), name="login"),
     path('auth/token/logout/', views.TokenDestroyView.as_view(), name="logout"),
]



