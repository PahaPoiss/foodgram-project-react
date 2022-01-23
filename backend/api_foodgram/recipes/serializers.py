import base64
import imghdr
import uuid

import six
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.serializers import (CustomUserSerializer,
                               RecipeEasyRetrieveSerializer)

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


# Рецепт-Ингредиент для чтения

class RecipeIngredientsRetrieveSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source=(
            'ingredient.measurement_unit'))

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


# Рецепт-Ингредиент для создания

class RecipeCreateIngridientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = (
            "id",
            "amount"
        )


# Для показа рецепта

class RecipeRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'tags', 'author', 'ingredients',
            'image', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsRetrieveSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_image(self, obj):
        return obj.image.url


# Для создания рецепта

class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeCreateIngridientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeRetrieveSerializer(
            instance, context=context).data

    def validate(self, data):
        ingredients = data['ingredients']
        list_ingredients = []
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля'
                )
            list_ingredients.append(ingredient['id'])
        if not list_ingredients:
            raise serializers.ValidationError(
                'Нужно добавить хотя бы один ингредиент'
            )
        if len(list_ingredients) != len(list(set(list_ingredients))):
            raise serializers.ValidationError(
                'Ингридиенты не должны повторяться'
            )
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время готовки должно быть больше нуля'
            )
        tags = data['tags']
        list_tags = []
        for tag in tags:
            list_tags.append(tag)
        if len(list_tags) != len(list(set(list_tags))):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return data


# Для избранного

class FavoriteCreateSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('user',)

    def create(self, validated_data):
        recipe_id = self.context['view'].kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context.get('request').user
        Favorite.objects.get_or_create(user=user, recipe=recipe)

        return recipe

    def validate(self, data):
        recipe_id = self.context['view'].kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context.get('request').user
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Нельзя добавить рецепт в избранное дважды'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeEasyRetrieveSerializer(
            instance, context=context).data


# Для корзины

class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('user',)

    def create(self, validated_data):
        recipe_id = self.context['view'].kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context.get('request').user
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)

        return recipe

    def validate(self, data):
        recipe_id = self.context['view'].kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Нельзя добавить рецепт в корзину дважды'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeEasyRetrieveSerializer(
            instance, context=context).data
