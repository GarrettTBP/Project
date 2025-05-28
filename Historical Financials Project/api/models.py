from django.db import models

class Property(models.Model):
    name = models.CharField(max_length=200)
    units = models.IntegerField()
    property_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Expense(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='expenses'
    )
    month = models.IntegerField()
    year = models.IntegerField()
    payroll = models.FloatField()
    marketing = models.FloatField()
    admin = models.FloatField()
    maintenance = models.FloatField()
    turnover = models.FloatField()
    utilities = models.FloatField()
    taxes = models.FloatField()
    insurance = models.FloatField()
    management_fees = models.FloatField()

class Unit(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='unit_entries'  # no longer 'units', to avoid the name clash
    )
    unit_number    = models.IntegerField()
    square_footage = models.FloatField()

    class Meta:
        unique_together = ('property', 'unit_number')

    def __str__(self):
        return f"{self.property.name} – Unit {self.unit_number}"