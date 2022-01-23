from django.db import models
from users.models import User


# Основные модели

# Тэг

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


# Ингредиент

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


# Рецепт

class Recipe(models.Model):
    name = models.CharField(max_length=250,
                            verbose_name='Название рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredients')

    tags = models.ManyToManyField(Tag,
                                  through='RecipeTags')

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')

    image = models.FileField()

    text = models.TextField()

    cooking_time = models.IntegerField()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


# Избранное

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="favouriter")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="favourited")


# Избранное

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="buyer")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="cart")


# Промежуточные модели


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class RecipeTags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'
