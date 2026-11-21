from django.urls import path
from . import views

urlpatterns = [
    path('max-login/', views.max_login, name='max-login'),
]