from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnamnesisViewSet

router = DefaultRouter()
router.register(r'anamnesis', AnamnesisViewSet, basename='anamnesis')

urlpatterns = [
    path('', include(router.urls)),
]