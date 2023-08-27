from django.contrib.auth import get_user_model
from django.db.models import Sum

from recipes.models import Ingredient


User = get_user_model()


def get_shoping_cart(user: User) -> str:
    """Получить список покупок.

    Args:
        user (User):
            Пользователь, для которого получаем список покупок.

    Returns:
        str:
            Список продуктов.
    """
    shopping_list = ['Ваш список покупок: \n']
    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values('name', 'measurement_unit')
        .annotate(amount=Sum('recipe__amount'))
    )
    ingredients_list = (
        f'{ingredient["name"]} ({ingredient["measurement_unit"]}) '
        f'- {ingredient["amount"]}'
        for ingredient in ingredients
    )
    shopping_list.extend(ingredients_list)
    shopping_list.append('\nПриятных покупок!')
    shopping_list.append('Ваш Foodgram.')
    return "\n".join(shopping_list)
