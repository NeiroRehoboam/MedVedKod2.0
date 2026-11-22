from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StartSessionView, SendMessageView, SessionViewSet, CompleteSessionView
)

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='sessions') 

urlpatterns = [
    path('sessions/start/', StartSessionView.as_view(), name='start-session'),
   # path('sessions/<int:session_id>/select-category/', SelectCategoryView.as_view()),
    path('sessions/<int:session_id>/message/', SendMessageView.as_view()),
    path('sessions/<int:session_id>/complete/', CompleteSessionView.as_view(), name='complete-session'),
    
    path('', include(router.urls)),
]