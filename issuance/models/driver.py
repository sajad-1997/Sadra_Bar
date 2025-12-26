from django.db import models
from django_jalali.db import models as jmodels

from .base import UserTrackingModel


class Driver(UserTrackingModel):
    name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=50, unique=True)
    father_name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = jmodels.jDateField(blank=True, null=True)
    residence = models.CharField(max_length=100, blank=True, null=True)
    certificate = models.CharField(max_length=50, unique=True)
    certificate_date = jmodels.jDateField(blank=True, null=True)
    driver_smart_card = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_policy_expiry = jmodels.jDateField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
