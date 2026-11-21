from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, FullRecordView

router = DefaultRouter()
router.register(r'patients', PatientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('full-record/', FullRecordView.as_view(), name='full-record'),
]