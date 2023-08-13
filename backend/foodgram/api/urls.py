from rest_framework import routers
from django.urls import path, include

from .views import TagViewSet, IngredientViewSet, RecipeViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/', include(router.urls)),
]
