from django.contrib import admin
from .models import Sender, Receiver, Driver, Vehicle


class SenderAdmin(admin.ModelAdmin):
    pass


class ReceiverAdmin(admin.ModelAdmin):
    pass


admin.site.register(Sender, SenderAdmin)
