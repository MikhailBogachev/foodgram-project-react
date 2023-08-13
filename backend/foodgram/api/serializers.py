from rest_framework import serializers
from django.db.models import F
from django.core.exceptions import ValidationError

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients
from api.core.validators import ingredients_validator, tags_exist_validator


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(), slug_field='id', many=True)
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, recipe: Recipe):
        """Получает список ингридиентов для рецепта.

        Args:
            recipe (Recipe): Запрошенный рецепт.

        Returns:
            QuerySet[dict]: Список ингридиентов в рецепте.
        """
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients
    
    def validate(self, data):
        """Проверка вводных данных при создании/редактировании рецепта.

        Args:
            data (OrderedDict): Вводные данные.

        Raises:
            ValidationError: Тип данных несоответствует ожидаемому.

        Returns:
            data (dict): Проверенные данные.
        """
        tags_ids: list[int] = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")

        if not tags_ids or not ingredients:
            raise ValidationError("Недостаточно данных.")

        tags = tags_exist_validator(tags_ids, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)

        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": self.context.get("request").user,
            }
        )
        return data

    
    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)
        objs = []

        for ingredient, amount in ingredients_data.values():
            objs.append(
                RecipeIngredients(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
            )

        RecipeIngredients.objects.bulk_create(objs)

        return recipe
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'name', 'image', 'text', 'cooking_time', 'ingredients', 'author')
