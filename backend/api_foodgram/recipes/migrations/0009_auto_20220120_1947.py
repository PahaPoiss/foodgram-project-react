# Generated by Django 2.2.16 on 2022-01-20 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_shoppingcart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='recipes.RecipeIngredients'),
        ),
    ]
