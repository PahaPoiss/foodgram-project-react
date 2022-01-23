from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import (IsAdminUser, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
from django.db.models import Sum
from .filters import RecipeFilter, IngredientFilter
from io import BytesIO
import os
import api_foodgram.settings as settings

from .models import (Recipe, RecipeIngredients, ShoppingCart, Tag, Ingredient, Favorite)
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          OwnerOrReadOnly)

from .serializers import (IngredientSerializer, ShoppingCartCreateSerializer, TagSerializer,
                          RecipeRetrieveSerializer,
                          RecipeCreateSerializer,
                          FavoriteCreateSerializer)


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
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    # search_fields = ('^name',)
    # filterset_fields = ('name',)

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

    # def fetch_pdf_resources(self, url, rel):
    #     if url.find(settings.MEDIA_URL) != -1:
    #         path = os.path.join(settings.MEDIA_ROOT, url.replace(settings.MEDIA_URL, ''))
    #     elif url.find(settings.STATIC_URL) != -1:
    #         path = os.path.join(settings.STATIC_ROOT, url.replace(settings.STATIC_URL, ''))
    #     else:
    #         path = None
    #     return path

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
            'ingredient__measurement_unit',
            ).annotate(total=Sum(
                'amount'))
        shopping_cart = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            shopping_cart.append(
                f"{name}: {total} {measurement_unit}\n"
            )
        response = HttpResponse(shopping_cart, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment;' 'filename="shopping_cart.txt"'
        )
        return response


@action(methods=['delete'], detail=True)
class FavoriteCreateViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteCreateSerializer
    queryset = Favorite.objects.all()
    permission_class = (IsAuthenticated,)

    def delete(self, request,  *args, **kwargs):
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

    def delete(self, request,  *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = Recipe.objects.get(id=recipe_id)
        user = request.user
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
