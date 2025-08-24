from django.contrib import admin
from .models import Sender, Receiver, Driver, Vehicle, Bijak
import django_jalali.admin as jadmin


class SenderAdmin(admin.ModelAdmin):
    pass


class ReceiverAdmin(admin.ModelAdmin):
    pass


class DriverAdmin(admin.ModelAdmin):
    pass


class VehicleAdmin(admin.ModelAdmin):
    pass


class BijakAdmin(admin.ModelAdmin):
    list_display = ('issuance_date',)


admin.site.register(Sender, SenderAdmin)
admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Bijak, BijakAdmin)
