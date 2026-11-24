from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API приложений
    path('api/auth/', include('auth_max.urls')),
    path('api/ai/', include('ai_assis.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/anamnesis/', include('anamnesis.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/dictionaries/', include('dictionaries.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG and settings.ENABLE_DEMO_LOGIN:
    urlpatterns += [path('api/auth/', include('auth_max.dev_urls'))]
