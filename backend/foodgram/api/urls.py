from rest_framework import routers
from django.urls import path, include

from .views import TagViewSet, IngredientViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('v1/', include(router.urls)),
]
