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
                                         through='RecipeIngredient')

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')

    tags = models.ManyToManyField(Tag)

    image = models.FileField()

    text = models.TextField()

    cooking_time = models.IntegerField()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favouriter')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favourited')

    class Meta:
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart')

    class Meta:
        unique_together = ('user', 'recipe')


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
