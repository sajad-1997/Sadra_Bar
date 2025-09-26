from django.contrib import admin
from .models import Customer, Driver, Vehicle, Bijak
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear


class BijakAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'issuance_date', 'sender', 'receiver', 'value')

    readonly_fields = ('tracking_code', 'issuance_date')

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)

        # گروه‌بندی روزانه
        daily = qs.annotate(day=TruncDay('issuance_date')).values('day').annotate(count=Count('id')).order_by('-day')

        # گروه‌بندی هفتگی
        weekly = qs.annotate(week=TruncWeek('issuance_date')).values('week').annotate(count=Count('id')).order_by(
            '-week')

        # گروه‌بندی ماهانه
        monthly = qs.annotate(month=TruncMonth('issuance_date')).values('month').annotate(count=Count('id')).order_by(
            '-month')

        # گروه‌بندی سالانه
        yearly = qs.annotate(year=TruncYear('issuance_date')).values('year').annotate(count=Count('id')).order_by(
            '-year')

        extra_context = extra_context or {}
        extra_context['daily_counts'] = daily
        extra_context['weekly_counts'] = weekly
        extra_context['monthly_counts'] = monthly
        extra_context['yearly_counts'] = yearly

        return super().changelist_view(request, extra_context=extra_context)


class CustomerAdmin(admin.ModelAdmin):
    pass


class DriverAdmin(admin.ModelAdmin):
    pass


class VehicleAdmin(admin.ModelAdmin):
    pass


admin.site.register(Bijak, BijakAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
