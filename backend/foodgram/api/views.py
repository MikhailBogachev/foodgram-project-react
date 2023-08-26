from django.db.models import Q
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from djoser.views import UserViewSet as DjoserUserViewSet

from api.paginators import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.core.mixins import AddOrDeleteRelationForUserViewMixin
from api.core.utils import get_shoping_cart
from users.models import Follow
from api.filters import IngredientFilter
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    FavoriteRecipe,
    ShoppingCart
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ReadRecipeSerializer,
    FollowSerializer
)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для получения тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для получения ингридиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)


class RecipeViewSet(
    viewsets.ModelViewSet,
    AddOrDeleteRelationForUserViewMixin
):
    """Контроллер для работы с рецептами"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    relation_serializer = ReadRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        author_id = self.request.query_params.get('author')
        list_tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')

        if author_id:
            queryset = queryset.filter(author=author_id)
        if list_tags:
            queryset = queryset.filter(tags__slug__in=list_tags)
        if user.is_anonymous:
            return queryset
        if is_favorited == '1':
            queryset = queryset.filter(in_favorites__user=user)
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(in_carts__user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True)
    def favorite(self, request, pk: int,
                 permission_classes=(IsAuthenticated,)) -> Response:
        """Добавить рецепт в избранное"""
        ...

    @favorite.mapping.post
    def add_recipe_to_favorites(self, request, pk: int) -> Response:
        """Добавить связь в модель избранных рецептов"""
        self.relation_model = FavoriteRecipe
        return self.add_relation(object_id=pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(self, request, pk: int) -> Response:
        """Удалить связь из модели избранных рецептов"""
        self.relation_model = FavoriteRecipe
        return self.delete_relation(Q(recipe__id=pk))

    @action(detail=True)
    def shopping_cart(self, request, pk: int,
                      permission_classes=(IsAuthenticated,)) -> Response:
        """Добавить рецепт в список покупок"""
        ...

    @shopping_cart.mapping.post
    def add_recipe_to_shopping_cart(self, request, pk: int) -> Response:
        """Добавить связь в модель списка покупок"""
        self.relation_model = ShoppingCart
        return self.add_relation(object_id=pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_shopping_cart(self, request, pk: int) -> Response:
        """Удалить связь из модели списка покупок"""
        self.relation_model = ShoppingCart
        return self.delete_relation(Q(recipe__id=pk))

    @action(methods=("get",), detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request) -> Response:
        """Получить список покупок."""
        return HttpResponse(
            get_shoping_cart(self.request.user),
            content_type="text.txt; charset=utf-8"
        )


class UserViewSet(DjoserUserViewSet, AddOrDeleteRelationForUserViewMixin):
    """Контроллер для работы с пользователями"""
    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    relation_serializer = FollowSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id: int) -> Response:
        """Подписаться на автора."""

    @subscribe.mapping.post
    def create_subscribe(self, request, id: int) -> Response:
        """Добавить связь в модель подписок"""
        self.relation_model = Follow
        return self.add_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id: int) -> Response:
        """Удалить связь из модель подписок"""
        self.relation_model = Follow
        return self.delete_relation(Q(following__id=id))

    @action(methods=("get",), detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request) -> Response:
        """Получить список покупок"""
        pages = self.paginate_queryset(
            User.objects.filter(following__user=self.request.user)
        )
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
