# Generated by Django 2.2.16 on 2022-01-12 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={},
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['name'], name='recipes_ing_name_164c6a_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['name'], name='recipes_tag_name_56fd94_idx'),
        ),
    ]
