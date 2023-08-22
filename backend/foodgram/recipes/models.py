from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image


User = get_user_model()


class Tag(models.Model):
    """Теги"""
    name = models.CharField(
        max_length=100,
        verbose_name='Тег'
    )
    hex_code = models.CharField(
        max_length=10,
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингридиента'
    )
    measurement_unit=models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепты"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredients",
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes'
    )
    cooking_time = models.IntegerField()

    # def save(self, *args, **kwargs) -> None:
    #     super().save(*args, **kwargs)
    #     image = Image.open(self.image.path)
    #     image.thumbnail(Tuples.RECIPE_IMAGE_SIZE)
    #     image.save(self.image.path)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

class RecipeIngredients(models.Model):
    """Ингредиенты для рецептов с количеством"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    amount = models.IntegerField()

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredient}"


class FavoriteRecipe(models.Model):
    """Избранные рецепты"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites'
    )
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique favorites'),
        )
    
    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    """Корзина покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts'
    )
    
    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
