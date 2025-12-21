from django.db import models


class InsuranceCompany(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, null=True)
    economic_code = models.CharField(max_length=50, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
