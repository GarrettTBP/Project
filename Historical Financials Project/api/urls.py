from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PropertyViewSet, ExpenseViewSet, UnitViewSet

router = DefaultRouter()
router.register('properties', PropertyViewSet)
router.register('expenses', ExpenseViewSet)
router.register('units',  UnitViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
