from django.urls import path
from . import views
from . import dev_views

urlpatterns = [
    path('max-login/', views.max_login),
    path('logout/', views.logout_view),
    path('me/', views.CurrentUserView.as_view()),
    path("demo/", dev_views.demo_login, name="demo-login"),
]
