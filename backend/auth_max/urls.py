from django.urls import path
from . import views

urlpatterns = [
    path('max-login/', views.max_login, name='max-login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'), 
]