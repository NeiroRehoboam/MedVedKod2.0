from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API приложений
    path('api/auth/', include('auth_max.urls')),
    path('api/ai/', include('ai_assis.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/anamnesis/', include('anamnesis.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/dictionaries/', include('dictionaries.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
 
    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]