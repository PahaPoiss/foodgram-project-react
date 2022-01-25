from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from api_foodgram.pagination import CustomPagination
from .filters import IngredientFilter, RecipeFilter
from .mixins import AddDeleteListMixin
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
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
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart',
            url_name='download')
    def download_shopping_cart(self, request):
        user = request.user
        recipes = RecipeIngredient.objects.filter(recipe__cart__user=user)
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


class FavoriteViewSet(AddDeleteListMixin, APIView):
    serializer_class = FavoriteCreateSerializer
    model_class = Favorite
    permission_class = (IsAuthenticated,)


class ShoppingCartViewSet(AddDeleteListMixin, APIView):
    serializer_class = ShoppingCartCreateSerializer
    model_class = ShoppingCart
    permission_class = (IsAuthenticated,)
