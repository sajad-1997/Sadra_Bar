from django.db.models.signals import post_save
from django.dispatch import receiver

from issuance.models import Bijak
from .models.company import InsuranceCompany
from .models.policy import InsurancePolicy
from .models.policy_type import InsurancePolicyType


@receiver(post_save, sender=Bijak.sender)
def create_insurance_for_bil(sender, instance, created, **kwargs):
    if created:
        # بررسی اینکه آیا رکورد بیمه وجود دارد
        if not InsurancePolicy.objects.filter(bil=instance).exists():
            # انتخاب شرکت بیمه پیش‌فرض (می‌توان بعداً انتخاب توسط کاربر)
            default_company = InsuranceCompany.objects.first()
            # انتخاب نوع بیمه پیش‌فرض
            default_policy_type = InsurancePolicyType.objects.first()
            # محاسبه مبلغ بیمه (مثلاً ثابت یا درصدی از کرایه)
            premium_amount = int(instance.freight_amount * 0.05)  # مثال: 5% کرایه

            # ایجاد رکورد بیمه
            InsurancePolicy.objects.create(
                bil=instance,
                insurance_company=default_company,
                policy_type=default_policy_type,
                cargo_value=instance.cargo_value,
                premium_amount=premium_amount,
                status='pending'
            )
