from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoutingResultViewSet

router = DefaultRouter()
router.register(r'results', RoutingResultViewSet)
urlpatterns = [path('', include(router.urls))]