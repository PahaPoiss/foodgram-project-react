from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_foodgram.pagination import CustomPagination

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)
from .permissions import IsAdminOrReadOnly, OwnerOrReadOnly
from .serializers import (FavoriteCreateSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeRetrieveSerializer,
                          ShoppingCartCreateSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        if user.is_anonymous:
            return queryset
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_favorited:
            queryset = queryset.filter(favourited__user=user)
        if is_in_shopping_cart:
            queryset = queryset.filter(cart__user=user)
        return queryset

    # Скачивание списка покупок
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart',
            url_name='download')
    def download_shopping_cart(self, request):
        user = request.user
        recipes = RecipeIngredients.objects.filter(recipe__cart__user=user)
        ingredients = recipes.values(
            'ingredient__name',
            'ingredient__measurement_unit',).annotate(total=Sum(
                'amount'))
        shopping_cart = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            shopping_cart.append(
                f"{name}: {total} {measurement_unit}\n"
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response


@action(methods=['delete'], detail=True)
class FavoriteCreateViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteCreateSerializer
    queryset = Favorite.objects.all()
    permission_class = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = Recipe.objects.get(id=recipe_id)
        user = request.user
        Favorite.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@action(methods=['delete'], detail=True)
class ShoppingCartCreateViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartCreateSerializer
    queryset = ShoppingCart.objects.all()
    permission_class = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = Recipe.objects.get(id=recipe_id)
        user = request.user
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
