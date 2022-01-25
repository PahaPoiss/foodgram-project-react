# Ff

from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=250,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=20,
                                        verbose_name='Единица измерения')

    class Meta:
        indexes = [models.Index(fields=['name', ])]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=50,
                            verbose_name='Название тега')

    color = models.CharField(unique=True, max_length=20,
                             verbose_name='HEX-код')

    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        indexes = [models.Index(fields=['name', ])]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=250,
                            verbose_name='Название рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')

    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    image = models.FileField(verbose_name='Картинка')

    text = models.TextField(verbose_name='Текст рецепта')

    cooking_time = models.IntegerField(verbose_name='Время приготовления')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favouriter',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favourited',
                               verbose_name='Рецепт')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['recipe', 'user'],
                                               name='unique_favorite')]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart',
                               verbose_name='Рецепт')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['recipe', 'user'],
                                               name='unique_cart')]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.IntegerField(verbose_name='Количество ингредиента')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient')]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
