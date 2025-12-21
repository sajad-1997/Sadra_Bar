from django.contrib.auth import get_user_model
from django.db import models

# از ارجاع رشته‌ای استفاده می‌کنیم به جای import مستقیم
# از 'issuance.Bijak' استفاده می‌کنیم تا circular dependency نشود
User = get_user_model()


class InsuranceCommissionAllocation(models.Model):
    invoice = models.ForeignKey('insurance.InsuranceInvoice', on_delete=models.CASCADE)
    bijak = models.ForeignKey('issuance.Bijak', on_delete=models.CASCADE)
    allocated_amount = models.BigIntegerField()
    allocated_date = models.DateTimeField(auto_now_add=True)
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    allocated_by_role = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bijak} - {self.allocated_amount}"
