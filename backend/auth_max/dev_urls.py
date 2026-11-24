from django.urls import path

from .dev_views import demo_login

urlpatterns = [
    path('demo/', demo_login, name='demo-login'),
]
