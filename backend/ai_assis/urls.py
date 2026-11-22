from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartSessionView, SendMessageView, SessionViewSet

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='sessions')

urlpatterns = [
    path('sessions/start/', StartSessionView.as_view(), name='start-session'),
    path('sessions/<int:session_id>/message/', SendMessageView.as_view(), name='send-message'),
   
    path('', include(router.urls)),
]