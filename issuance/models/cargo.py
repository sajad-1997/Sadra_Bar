from django.db import models

from .base import UserTrackingModel


class Cargo(UserTrackingModel):
    name = models.CharField(max_length=50)
    weight = models.CharField(max_length=5)
    package_type = models.CharField(max_length=10, blank=True, null=True)
    number_of_packaging = models.CharField(max_length=3, blank=True, null=True)
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)

    def __str__(self):
        return self.name
