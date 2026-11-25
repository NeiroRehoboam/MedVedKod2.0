from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, PreferredPaymentView

router = DefaultRouter()

# CRUD пациентов
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    # путь раньше роутера, иначе `me` уйдёт в detail-шаблон как pk
    path(
        'patients/me/preferred-payment/',
        PreferredPaymentView.as_view(),
        name='preferred-payment-update',
    ),
    path('', include(router.urls)),
]
