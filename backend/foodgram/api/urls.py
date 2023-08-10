from rest_framework import routers
from django.urls import path, include

from .views import TagViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('v1/', include(router.urls)),
]
