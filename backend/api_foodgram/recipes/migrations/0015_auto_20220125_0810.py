# Generated by Django 2.2.16 on 2022-01-25 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20220125_0808'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='unique_recipe_ingredient',
        ),
    ]
