from django.db import models

# از ارجاع رشته‌ای برای Bijak در صورت اضافه شدن FK استفاده می‌کنیم
from .company import InsuranceCompany


class InsuranceClaim(models.Model):
    STATUS_CHOICES = [
        ('open', 'باز شده'),
        ('in_review', 'در حال بررسی'),
        ('paid', 'پرداخت شده'),
        ('rejected', 'رد شده'),
    ]

    insurance_company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE)
    bil_id = models.IntegerField()  # در آینده می‌توان FK به 'issuance.Bijak' تبدیل کرد
    # bijak = models.ForeignKey('issuance.Bijak', on_delete=models.CASCADE, null=True)
    claim_no = models.CharField(max_length=100)
    claim_amount = models.BigIntegerField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return self.claim_no
