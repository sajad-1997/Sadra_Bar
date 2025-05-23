from django import forms
from .models import Sender, Receiver, Driver, Vehicle, Shipment


class SenderForm(forms.ModelForm):
    class Meta:
        model = Sender
        fields = '__all__'


class ReceiverForm(forms.ModelForm):
    class Meta:
        model = Receiver
        fields = '__all__'


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'
        widgets = {
            'birth_date': forms.TextInput(attrs={'class': 'persian-date-picker'}),
            'license_issue_date': forms.TextInput(attrs={'class': 'persian-date-picker'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_code', 'date']
        widgets = {
            'date': forms.TextInput(attrs={'class': 'persian-date-picker'}),
        }
