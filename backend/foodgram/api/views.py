from datetime import datetime

from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, FavoriteRecipe, ShoppingCart
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, ShortRecipeSerializer
from api.core.mixins import AddOrDeleteRelationForUserViewMixin
from api.core.utils import get_shoping_cart
from django.http.response import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для получения тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Контроллер для получения ингридиентов"""
    queryset = Ingredient.objects.all()
    serializer_class=IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet, AddOrDeleteRelationForUserViewMixin):
    """Контроллер для работы с рецептами"""
    queryset =  Recipe.objects.all()
    serializer_class = RecipeSerializer
    relation_serializer = ShortRecipeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        author_id = self.request.query_params.get('author')
        list_tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')

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
    def favorite(self, request, pk: int) -> Response:
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
    def shopping_cart(self, request, pk: int) -> Response:
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

    # TODO refactor
    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request) -> Response:
        """Получить список покупок."""
        return HttpResponse(
            get_shoping_cart(self.request.user),
            content_type="text.txt; charset=utf-8"
        )
