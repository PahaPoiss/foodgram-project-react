# Generated by Django 2.2.16 on 2022-01-24 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20220120_1951'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredients',
            new_name='RecipeIngredient',
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together={('recipe', 'ingredient')},
        ),
    ]
