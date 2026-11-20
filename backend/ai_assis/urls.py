from django.urls import path
from .views import StartConsultationView, SendMessageView

urlpatterns = [
    path('consultations/start/', StartConsultationView.as_view(), name='start-consultation'),
    path('consultations/<int:consultation_id>/message/', SendMessageView.as_view(), name='send-message'),
]