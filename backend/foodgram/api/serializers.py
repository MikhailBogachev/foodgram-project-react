from collections import OrderedDict
import base64

from rest_framework import serializers
from django.db.models import F, QuerySet
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients
from users.models import Follow


User = get_user_model()


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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("is_subscribed",)

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с запрошенными полями."""
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def get_is_subscribed(self, author: User) -> bool:
        """Получает флаг подписки на автора.

        Args:
            user (User): Автор.

        Returns:
            bool: True - подписка есть, False - нет.
        """
        # user = self.context.get('view').request.user
        # if user.is_anonymous or user == author:
        #     return False
        # return True
        print(self.context['request'].user)
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follow.objects.filter(
                user=self.context['request'].user,
                following=author
            ).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
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
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Получает флаг избранного рецепта

        Args:
            recipe (Recipe): Рецепт.

        Returns:
            (bool): True - избранный, False - нет
        """
        user = self.context.get('view').request.user

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
        user = self.context.get('view').request.user

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
        ingredients: list[dict[str, int]] = self.initial_data.get(
            'ingredients'
        )

        if not tags or not ingredients:
            raise ValidationError('Отсутствуют теги и/или ингредиенты')

        existing_tags = Tag.objects.filter(id__in=tags)
        if len(tags) != len(existing_tags):
            raise ValidationError('Такой тег не существует')

        ingredients_tmp = {}
        for ing in ingredients:
            if int(ing['amount']) < 1:
                raise ValidationError(
                    'Кол-во ингредиента не может быть меньше 1'
                )
            ingredients_tmp[ing['id']] = ing['amount']
        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredients_tmp.keys()
        )
        if len(ingredients_tmp) != len(existing_ingredients):
            raise ValidationError('Такого ингредиента не существует')
        for ing in existing_ingredients:
            ingredients_tmp[ing.pk] = (ing, ingredients_tmp[ing.pk])
        data.update(
            {
                'tags': existing_tags,
                'ingredients': ingredients_tmp,
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
                RecipeIngredients(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
                for ingredient, amount in ingredients_data.values()
            ]
        )
        return recipe

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'name', 'image', 'text', 'cooking_time',
            'ingredients', 'author', 'is_favorited', 'is_in_shopping_cart'
        )


class RecipeReadSerializer(RecipeSerializer):
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для сериалайзера модели Follow.
    """
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class FollowSerializer(UserSerializer):
    """Сериализатор подписок"""

    recipes = ReadRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("__all__",)

    def get_is_subscribed(*args) -> bool:
        """Проверка подписки пользователей.

        Переопределённый метод родительского класса для уменьшения нагрузки,
        так как в текущей реализации всегда вернёт `True`.

        Returns:
            bool: True
        """
        return True

    def get_recipes_count(self, author: User) -> int:
        """Получить кол-во рецептов автора.

        Args:
            obj (User): Автор.

        Returns:
            int: Количество рецептов автора.
        """
        return author.recipes.count()
