from django.utils.datastructures import MultiValueDictKeyError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')

    def validate(self, data):
        if not data['first_name'] or len(data['first_name']) == 0:
            raise serializers.ValidationError(
                'Обязательное поле.')
        if not data['last_name'] or len(data['last_name']) == 0:
            raise serializers.ValidationError(
                'Обязательное поле.')
        if not data['username'] or len(data['username']) == 0:
            raise serializers.ValidationError(
                'Обязательное поле.')
        if not data['email'] or len(data['email']) == 0:
            raise serializers.ValidationError(
                'Обязательное поле.')
        if not data['password'] or len(data['password']) == 0:
            raise serializers.ValidationError(
                'Обязательное поле.')
        return data


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(author=obj, user=user).exists()


# Упрощённый для показа рецепта

class RecipeEasyRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time',
        )


# Для показа подписок

class FollowRetrieveSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'recipes', 'recipes_count',
                  'is_subscribed',)

    def get_recipes(self, obj):
        try:
            limit = self.context.get('request').query_params['recipes_limit']
        except MultiValueDictKeyError:
            limit = 10
        queryset = Recipe.objects.filter(author=obj)[:int(limit)]
        return RecipeEasyRetrieveSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(author=obj, user=user).exists()


# Для создания подписки

class FollowCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('author',)

    def create(self, validated_data):
        author_id = self.context['view'].kwargs['author_id']
        author = User.objects.get(id=author_id)
        user = self.context.get('request').user
        Follow.objects.get_or_create(author=author, user=user)

        return author

    def validate(self, data):
        author_id = self.context['view'].kwargs['author_id']
        author = User.objects.get(id=author_id)
        user = self.context.get('request').user
        if author == user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'Нельзя подписаться на одного автора дважды'
            )

        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowRetrieveSerializer(
            instance, context=context).data
