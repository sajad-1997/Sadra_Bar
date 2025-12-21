from django.db import models

from .contract import InsuranceContract
from .policy_type import InsurancePolicyType


class InsuranceRate(models.Model):
    contract = models.ForeignKey(InsuranceContract, on_delete=models.CASCADE)
    policy_type = models.ForeignKey(InsurancePolicyType, on_delete=models.CASCADE)
    base_premium = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_premium = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    max_premium = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.contract} - {self.policy_type}"
