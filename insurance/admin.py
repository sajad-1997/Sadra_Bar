from django.contrib import admin

from .models.alert import InsuranceAlert
from .models.commission import InsuranceCommissionAllocation
from .models.company import InsuranceCompany
from .models.contract import InsuranceContract
from .models.invoice import InsuranceInvoice
from .models.payment import InsurancePaymentTracking
from .models.policy import InsurancePolicy
from .models.policy_type import InsurancePolicyType


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'economic_code', 'status')
    search_fields = ('name', 'code', 'economic_code', 'national_id')
    list_filter = ('status',)


@admin.register(InsuranceContract)
class InsuranceContractAdmin(admin.ModelAdmin):
    list_display = ('contract_no', 'insurance_company', 'start_date', 'end_date', 'max_coverage_display')
    search_fields = ('contract_no', 'insurance_company__name')
    list_filter = ('insurance_company',)

    def max_coverage_display(self, obj):
        # اگر فیلد max_coverage در مدل وجود ندارد، مقدار مناسب یا محاسبه‌ای قرار دهید
        return getattr(obj, 'max_coverage', None)
    max_coverage_display.short_description = 'حداکثر پوشش'


@admin.register(InsurancePolicyType)
class InsurancePolicyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_required_for_bil')
    search_fields = ('name',)


@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ('bil_display', 'insurance_company', 'policy_type', 'status', 'premium_amount', 'cargo_value')
    search_fields = ('policy_number', 'insurance_company__name')
    list_filter = ('status', 'policy_type', 'insurance_company')

    def bil_display(self, obj):
        # مقدار مناسب برای bil، در صورت وجود فیلد policy_number
        return getattr(obj, 'policy_number', None)
    bil_display.short_description = 'BIL'


@admin.register(InsuranceInvoice)
class InsuranceInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'insurance_company', 'issue_date', 'total_amount', 'status')
    search_fields = ('invoice_number', 'insurance_company__name')
    list_filter = ('status', 'insurance_company')


@admin.register(InsuranceCommissionAllocation)
class InsuranceCommissionAllocationAdmin(admin.ModelAdmin):
    list_display = ('bil_display', 'invoice', 'allocated_amount', 'allocated_date', 'allocated_by')
    search_fields = ('invoice__invoice_number', 'allocated_by__username')

    def bil_display(self, obj):
        # اگر فیلد bil در مدل وجود ندارد، مقدار مناسب را جایگزین کنید
        return getattr(obj, 'bil', None)
    bil_display.short_description = 'BIL'


@admin.register(InsurancePaymentTracking)
class InsurancePaymentTrackingAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'paid_amount', 'remaining_amount', 'payment_date', 'paid_by')
    search_fields = ('invoice__invoice_number', 'paid_by__username')


@admin.register(InsuranceAlert)
class InsuranceAlertAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'alert_time', 'status')
    list_filter = ('status',)
