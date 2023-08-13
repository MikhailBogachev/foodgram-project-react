from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    """Теги"""
    name=models.CharField(
        max_length=100,
        verbose_name='Тег'
    )
    hex_code=models.CharField(
        max_length=10,
        verbose_name='Цветовой HEX-код'
    )
    slug=models.SlugField(
        unique=True
    )


class Ingredient(models.Model):
    """Ингредиенты"""
    name=models.CharField(
        max_length=100,
        verbose_name='Название ингридиента'
    )
    measurement_unit=models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )


class Recipe(models.Model):
    """Рецепты"""
    author=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name=models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    image=models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True
    )
    text=models.TextField()
    ingredients=models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name='recipes'
    )
    tags=models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes'
    )
    cooking_time=models.IntegerField()


class RecipeIngredients(models.Model):
    """Ингредиенты для рецептов с количеством"""
    recipe=models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    ingredient=models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    amount=models.IntegerField()
