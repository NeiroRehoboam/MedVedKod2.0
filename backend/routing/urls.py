from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoutingViewSet

router = DefaultRouter()
router.register(r'routing', RoutingViewSet)
urlpatterns = [path('', include(router.urls))]