from django.core.exceptions import ValidationError
from recipes.models import Tag
def ingredients_validator(
    ingredients,
    Ingredient,
):
    """Проверяет список ингридиентов.

    Если повторяется ингридиенты, то сохраняется последний, считаем,
    что пользователь забыл, что уже указывал ингридиент и написал его опять.

    Args:
        ingredients (list[dict[str, str | int]]):
            Список ингридиентов.
            Example: [{'amount': '5', 'id': 2073},]
        Ingredient (Ingredient):
            Модель ингридиентов во избежании цикличного импорта.

    Raises:
        ValidationError: Ошибка в переданном списке ингридиентов.

    Returns:
        dict[int, tuple[Ingredient, int]]:
    """
    if not ingredients:
        raise ValidationError("Не указаны ингридиенты")

    valid_ings = {}

    for ing in ingredients:
        if not (isinstance(ing["amount"], int) or ing["amount"].isdigit()):
            raise ValidationError("Неправильное количество ингидиента")

        valid_ings[ing["id"]] = int(ing["amount"])
        if valid_ings[ing["id"]] <= 0:
            raise ValidationError("Неправильное количество ингридиента")

    if not valid_ings:
        raise ValidationError("Неправильные ингидиенты")

    db_ings = Ingredient.objects.filter(pk__in=valid_ings.keys())
    if not db_ings:
        raise ValidationError("Неправильные ингидиенты")

    for ing in db_ings:
        valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

    return valid_ings


def tags_exist_validator(tags_ids, Tag) :
    """Проверяет наличие тэгов с указанными id.

    Args:
        tags_ids (list[int | str]): Список id.
        Tag (Tag): Модель тэгов во избежании цикличного импорта.

    Raises:
        ValidationError: Тэга с одним из указанных id не существует.
    """
    if not tags_ids:
        raise ValidationError("Не указаны тэги")

    tags = Tag.objects.filter(id__in=tags_ids)

    if len(tags) != len(tags_ids):
        raise ValidationError("Указан несуществующий тэг")

    return tags