from django.contrib import admin
from .models import Sender, Receiver, Driver, Vehicle, BijakForm


class SenderAdmin(admin.ModelAdmin):
    pass


class ReceiverAdmin(admin.ModelAdmin):
    pass


class DriverAdmin(admin.ModelAdmin):
    pass


class VehicleAdmin(admin.ModelAdmin):
    pass


class BijakAdmin(admin.ModelAdmin):
    pass


admin.site.register(Sender, SenderAdmin)
admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(BijakForm, BijakAdmin)
