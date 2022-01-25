from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User
from users.serializers import (CustomUserSerializer,
                               RecipeEasyRetrieveSerializer)
from .fields import Base64ImageField
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeIngredientsRetrieveSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source=(
            'ingredient.measurement_unit'))

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateIngridientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


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
        queryset = RecipeIngredient.objects.filter(recipe=obj)
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
            RecipeIngredient.objects.create(
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
        RecipeIngredient.objects.filter(recipe=instance).delete()
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


class FavoriteCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в избранное дважды'
            )
        ]

    def to_representation(self, instance):
        return RecipeEasyRetrieveSerializer(instance.recipe).data


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в корзину дважды'
            )
        ]

    def to_representation(self, instance):
        return RecipeEasyRetrieveSerializer(instance.recipe).data
