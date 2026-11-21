from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API приложений
    path('api/auth/', include('auth_max.urls')),
    path('api/ai/', include('ai_assis.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/anamnesis/', include('anamnesis.urls')),
    path('api/routing/', include('routing.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]