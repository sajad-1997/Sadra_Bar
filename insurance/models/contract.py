from django.db import models

from .company import InsuranceCompany


class InsuranceContract(models.Model):
    insurance_company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE)
    contract_no = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    attachment = models.FileField(upload_to="insurance/contracts/", blank=True, null=True)

    def __str__(self):
        return f"{self.insurance_company.name} - {self.contract_no}"
