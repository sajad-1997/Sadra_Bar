from django.db import models


class InsurancePolicyType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_required_for_bil = models.BooleanField(default=False)

    def __str__(self):
        return self.name
