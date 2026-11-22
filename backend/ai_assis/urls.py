from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartSessionView, SendMessageView, BaseQuestionViewSet, SelectCategoryView

router = DefaultRouter()
router.register(r'base-questions', BaseQuestionViewSet, basename='base-questions')

urlpatterns = [
    path('', include(router.urls)),
    path('sessions/start/', StartSessionView.as_view()),
    path('sessions/<int:session_id>/select-category/', SelectCategoryView.as_view()), # <-- Новый маршрут
    path('sessions/<int:session_id>/message/', SendMessageView.as_view()),
]