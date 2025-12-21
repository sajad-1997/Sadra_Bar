from celery import shared_task
from django.utils import timezone

from .models.alert import InsuranceAlert
from .models.invoice import InsuranceInvoice


@shared_task
def check_insurance_debts():
    """
    بررسی بدهی های بیمه و ایجاد رکورد هشدار برای صورت‌حساب های باقی‌مانده
    """
    now = timezone.now()
    unpaid_invoices = InsuranceInvoice.objects.filter(status__in=['pending', 'partially_paid'])

    for invoice in unpaid_invoices:
        # ثبت هشدار جدید
        alert, created = InsuranceAlert.objects.get_or_create(
            invoice=invoice,
            alert_time=now,
            defaults={'status': 'pending'}
        )
