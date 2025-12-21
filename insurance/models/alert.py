from django.db import models

from .invoice import InsuranceInvoice


class InsuranceAlert(models.Model):
    invoice = models.ForeignKey(InsuranceInvoice, on_delete=models.CASCADE)
    alert_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('pending', 'Pending')], default='pending')

    def __str__(self):
        return f"Alert for {self.invoice} at {self.alert_time}"
