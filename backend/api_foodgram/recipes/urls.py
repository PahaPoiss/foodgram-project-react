from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipes.views import (RecipeViewSet, IngredientViewSet,
                           TagViewSet, FavoriteCreateViewSet,
                           ShoppingCartCreateViewSet)


router = DefaultRouter()

router.register('recipes', RecipeViewSet)
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
