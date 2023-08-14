from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, FavoriteRecipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, ShortRecipeSerializer
from api.core.mixins import AddOrDeleteRelationForUserViewMixin


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
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True)
    def favorite(self, request, pk: int) -> Response:
        """"""

    @favorite.mapping.post
    def recipe_to_favorites(self, request, pk: int) -> Response:
        self.relation_model = FavoriteRecipe
        return self.add_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(self, request, pk) -> Response:
        self.relation_model = FavoriteRecipe
        return self.delete_relation(Q(recipe__id=pk))
