# Generated by Django 2.2.16 on 2022-01-25 05:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20220125_0813'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='unique_recipe_ingredient',
        ),
    ]
