from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscribeListViewSet,
    SubscribeViewSet,
    TagViewSet,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

subscribe_url = [
    path(r'users/subscriptions/',
         SubscribeListViewSet.as_view({'get': 'list'})),
    path(r'users/<int:user_id>/subscribe/',
         SubscribeViewSet.as_view()),
]


urlpatterns = [
    path('', include(subscribe_url)),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
