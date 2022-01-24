from django.urls import include, path
from recipes.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                           ShoppingCartViewSet, TagViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavoriteViewSet.as_view(), basename='favorite')
# router.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     ShoppingCartViewSet.as_view(), basename='shoppingcart')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartViewSet.as_view()),
    path('', include(router.urls)),
]
