from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnamnesisViewSet  # Импортируем ТОЛЬКО один класс

router = DefaultRouter()
router.register(r'anamnesis', AnamnesisViewSet, basename='anamnesis')

urlpatterns = [path('', include(router.urls))]