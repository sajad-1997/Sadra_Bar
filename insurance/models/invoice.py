from django.db import models

from .company import InsuranceCompany


class InsuranceInvoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid')
    ]

    invoice_number = models.CharField(max_length=100)
    insurance_company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE)
    issue_date = models.DateField()
    received_date = models.DateField(blank=True, null=True)
    total_amount = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attachment = models.FileField(upload_to="insurance/invoices/", blank=True, null=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.insurance_company.name}"
