# api/views.py

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Property, Expense, Unit 
from .serializers import PropertySerializer, ExpenseSerializer, UnitSerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset         = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [AllowAny]

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]        # ← allow anyone

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]        # ← allow anyone
