from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register(
    r'chronic-diseases',
    ChronicDiseaseViewSet,
    basename='chronic-diseases'
)

router.register(r'allergy-types', AllergyTypeViewSet, basename='allergy-types')
router.register(r'hereditary', HereditaryDiseaseViewSet, basename='hereditary')
router.register(r'specialties', SpecialtyViewSet, basename='specialties')
router.register(r'allergens', AllergyReferenceViewSet, basename='allergens')
router.register(r'medications', MedicationReferenceViewSet,
                basename='medications')
router.register(r'complaint-categories', ComplaintCategoryViewSet,
                basename='complaint-categories')
router.register(r'payment-types', PaymentTypeViewSet, basename='payment-types')

urlpatterns = [
    path('', include(router.urls)),
]
