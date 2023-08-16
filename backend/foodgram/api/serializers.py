from collections import OrderedDict

from rest_framework import serializers
from django.db.models import F, QuerySet
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(), slug_field='id', many=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        """Получает список ингридиентов для рецепта.

        Args:
            recipe (Recipe): Рецепт.

        Returns:
            QuerySet[dict]: Список ингридиентов и их количество в рецепте.
        """
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Получает флаг избранного рецепта

        Args:
            recipe (Recipe): Рецепт.

        Returns:
            (bool): True - избранный, False - нет
        """
        user = self.context.get("view").request.user

        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()
    
    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Получает флаг рецепта в списке покупок

        Args:
            recipe (Recipe): Рецепт.

        Returns:
            (bool): True - в списке покупок, False - нет
        """
        user = self.context.get("view").request.user

        if user.is_anonymous:
            return False
        return user.carts.filter(recipe=recipe).exists()
    
    def validate(self, data: OrderedDict) -> dict:
        """Валидация полученных данных о рецепте.

        Args:
            data (OrderedDict): Полученные данные.

        Returns:
            data (dict): Валидные данные.

        Raises:
            ValidationError: Полученные данные не овтечают требованиям.
        """
        tags: list[int] = self.initial_data.get('tags')
        ingredients: list[dict[str, int]] = self.initial_data.get('ingredients')

        if not tags or not ingredients:
            raise ValidationError("Отсутствуют теги и/или ингредиенты")
        
        existing_tags = Tag.objects.filter(id__in=tags)
        if len(tags) != len(existing_tags):
            raise ValidationError("Такой тег не существует")

        ingredients_tmp = {}
        for ing in ingredients:
            if ing['amount'] < 1:
                raise ValidationError("Кол-во ингредиента не может быть меньше 1")
            ingredients_tmp[ing['id']] = ing['amount']
        existing_ingredients = Ingredient.objects.filter(id__in=ingredients_tmp.keys())
        if len(ingredients_tmp) != len(existing_ingredients):
            raise ValidationError("Такого ингредиента не существует")
        for ing in existing_ingredients:
            ingredients_tmp[ing.pk] = (ing, ingredients_tmp[ing.pk])
        data.update(
            {
                "tags": existing_tags,
                "ingredients": ingredients_tmp,
            }
        )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(recipe=recipe, ingredient=ingredient, amount=amount)
                for ingredient, amount in ingredients_data.values()
            ]
        )
        return recipe
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'name', 'image', 'text', 'cooking_time', 'ingredients', 'author', 'is_favorited', 'is_in_shopping_cart')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Определён укороченный набор полей для некоторых эндпоинтов.
    """
    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)
