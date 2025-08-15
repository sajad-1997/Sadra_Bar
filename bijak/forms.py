from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from .models import Sender, Receiver, Driver, Vehicle, Cargo, BijakForm


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


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = '__all__'


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = BijakForm
        fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'

    def __int__(self, *args, **kwargs):
        super(ShipmentForm, self).__init__(*args, **kwargs)
        self.fields['issuance_date'] = JalaliDateField(label=('تاریخ صدور'),
                                                       widget=AdminJalaliDateWidget)

# class BijakForm(forms.ModelForm):
#     class Meta:
#         model = BijakForm
#         fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'
#         widgets = {
#             'issuance_date': forms.TextInput(attrs={
#                 'class': 'form-control persian-date-picker',
#                 'placeholder': 'تاریخ را انتخاب کنید'}),
#         }

# class BijakForm(forms.ModelForm):
#     sender = forms.ModelChoiceField(
#         queryset=Sender.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         required=False
#     )
#     receiver = forms.ModelChoiceField(
#         queryset=Receiver.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         required=False
#     )
#
#     class Meta:
#         model = BijakForm
#         fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'

# class BijakForm(forms.ModelForm):
#     sender = forms.ModelChoiceField(
#         queryset=Sender.objects.all(),
#         empty_label="-- انتخاب فرستنده --",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     receiver = forms.ModelChoiceField(
#         queryset=Receiver.objects.all(),
#         empty_label="-- انتخاب گیرنده --",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     driver = forms.ModelChoiceField(
#         queryset=Driver.objects.all(),
#         empty_label="-- انتخاب راننده --",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     vehicle = forms.ModelChoiceField(
#         queryset=Vehicle.objects.all(),
#         empty_label="-- انتخاب خودرو --",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#
#     class Meta:
#         model = BijakForm
#         fields = ['tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee']
#     widgets = {
#         'issuance_date': forms.TextInput(attrs={'class': 'persian-date-picker'}),
#     }
