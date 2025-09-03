from django.contrib import admin
from .models import Customer, Driver, Vehicle, Bijak
import django_jalali.admin as jadmin


class CustomerAdmin(admin.ModelAdmin):
    pass


class DriverAdmin(admin.ModelAdmin):
    pass


class VehicleAdmin(admin.ModelAdmin):
    pass


class BijakAdmin(admin.ModelAdmin):
    list_display = ('issuance_date',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Bijak, BijakAdmin)
