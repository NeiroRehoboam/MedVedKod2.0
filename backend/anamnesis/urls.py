from django.urls import path
from .views import AnamnesisView

urlpatterns = [
    path("anamnesis/", AnamnesisView.as_view(), name="anamnesis"),
]