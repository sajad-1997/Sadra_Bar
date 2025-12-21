from django.db import models

# از ارجاع رشته‌ای برای Bijak استفاده می‌کنیم
from .company import InsuranceCompany
from .policy_type import InsurancePolicyType


class InsurancePolicy(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('issued', 'Issued'),
        ('confirmed', 'Confirmed')
    ]

    bijak = models.OneToOneField('issuance.Bijak', on_delete=models.CASCADE)
    insurance_company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE)
    policy_type = models.ForeignKey(InsurancePolicyType, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    cargo_value = models.BigIntegerField()
    premium_amount = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    policy_number = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(upload_to="insurance/policies/", blank=True, null=True)

    def __str__(self):
        return f"{self.bijak} - {self.insurance_company.name}"
