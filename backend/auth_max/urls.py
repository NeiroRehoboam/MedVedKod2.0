from django.urls import path
from . import views
urlpatterns = [
    path('max-login/', views.max_login),
    path('logout/', views.logout_view),
    path('me/', views.CurrentUserView.as_view()),
]