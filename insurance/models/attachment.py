from django.db import models

from .invoice import InsuranceInvoice


class InsuranceInvoiceAttachment(models.Model):
    invoice = models.ForeignKey(InsuranceInvoice, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="insurance/invoices_pdf/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.invoice} - {self.uploaded_at}"
