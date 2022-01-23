from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (FavoriteCreateViewSet, IngredientViewSet,
                           RecipeViewSet, ShoppingCartCreateViewSet,
                           TagViewSet)

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteCreateViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartCreateViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
