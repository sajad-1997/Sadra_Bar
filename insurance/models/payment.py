from django.contrib.auth import get_user_model
from django.db import models

from .invoice import InsuranceInvoice

User = get_user_model()


class InsurancePaymentTracking(models.Model):
    invoice = models.ForeignKey(InsuranceInvoice, on_delete=models.CASCADE)
    paid_amount = models.BigIntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paid_by_role = models.CharField(max_length=100, blank=True, null=True)
    remaining_amount = models.BigIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.invoice} - {self.paid_amount}"
