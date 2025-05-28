from rest_framework import serializers
from .models import Property, Expense, Unit

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Unit
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = '__all__'