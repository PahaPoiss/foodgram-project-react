from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngridientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'image',
                    'text', 'cooking_time', 'favorite_count')
    search_fields = ('name',)
    list_filter = ('name', 'author',)
    inlines = (RecipeIngridientsInline,)

    def favorite_count(self, obj):
        result = Favorite.objects.values('recipe_id').filter(
            recipe=obj).distinct().count()

        return result


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
