from django.urls import path
from .views import StartSessionView, SendMessageView
urlpatterns = [
    path('sessions/start/', StartSessionView.as_view()),
    path('sessions/<int:session_id>/message/', SendMessageView.as_view()),
]