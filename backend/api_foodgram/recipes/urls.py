from django.urls import include, path
from recipes.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                           ShoppingCartViewSet, TagViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view(),
         name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view(), name='shopping_cart'),
    path('', include(router.urls)),
]
