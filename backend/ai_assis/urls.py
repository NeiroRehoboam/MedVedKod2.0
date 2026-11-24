from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompleteSessionView,
    InitialQuestionView,
    SendMessageView,
    SessionResultView,
    SessionViewSet,
    StartSessionView,
    UpdateSessionAnswerView,
)

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='sessions')

urlpatterns = [
    path('sessions/start/', StartSessionView.as_view(), name='start-session'),
    path('sessions/<int:session_id>/initial-question/', InitialQuestionView.as_view(), name='session-initial-question'),
    # результат сессии по id
    path('sessions/<int:session_id>/result/', SessionResultView.as_view(), name='session-result'),
    path('sessions/<int:session_id>/message/', SendMessageView.as_view(), name='send-message'),
    # исправление ответа в незавершённой сессии
    path(
        'sessions/<int:session_id>/questions/<int:question_id>/',
        UpdateSessionAnswerView.as_view(),
        name='session-answer-update',
    ),
    path('sessions/<int:session_id>/complete/', CompleteSessionView.as_view(), name='complete-session'),
    path('', include(router.urls)),
]
