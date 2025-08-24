from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from .models import Sender, Receiver, Driver, Vehicle, Cargo, Bijak
import jdatetime
from jdatetime import date


# 🔹 تابع تبدیل اعداد فارسی به انگلیسی
def persian_to_english_numbers(value: str) -> str:
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    trans_table = str.maketrans(persian_digits, english_digits)
    return value.translate(trans_table)


# 🔹 کلاس پایه برای فرم‌ها (اعمال فقط روی فیلدهای مشخص عددی)
class PersianNumberFormMixin:
    numeric_fields = []  # لیست فیلدهایی که باید تبدیل شوند

    def clean(self):
        cleaned_data = super().clean()
        for field in self.numeric_fields:
            value = cleaned_data.get(field)
            if isinstance(value, str):
                cleaned_data[field] = persian_to_english_numbers(value)
        return cleaned_data


def persian_to_gregorian(jalali_str):
    # فرض می‌کنیم ورودی کاربر: ۱۴۰۳/۰۶/۰۱
    jalali_str = persian_to_english_numbers(jalali_str)  # تبدیل اعداد
    year, month, day = map(int, jalali_str.split('/'))
    g_date = jdatetime.date(year, month, day).togregorian()
    return g_date


class SenderForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['national_id', 'postal', 'phone']

    class Meta:
        model = Sender
        fields = '__all__'


class ReceiverForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['national_id', 'postal', 'phone']

    class Meta:
        model = Receiver
        fields = '__all__'


class DriverForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['national_id', 'birth_date', 'phone', 'phone2', 'certificate', 'certificate_date']

    class Meta:
        model = Driver
        fields = '__all__'

    def clean_birth_date(self):
        data = self.cleaned_data['birth_date']
        if isinstance(data, str):
            return persian_to_gregorian(data)
        return data

    def clean_certificate_date(self):
        data = self.cleaned_data['certificate_date']
        if isinstance(data, str):
            return persian_to_gregorian(data)
        return data


class VehicleForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['license_plate_three_digit', 'license_plate_two_digit', 'license_plate_series']

    class Meta:
        model = Vehicle
        fields = '__all__'


class CargoForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['weight', 'number_of_packaging']

    class Meta:
        model = Cargo
        fields = '__all__'


class ShipmentForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['tracking_code', 'issuance_date', 'value', 'insurance', 'loading_fee', ]

    class Meta:
        model = Bijak
        fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'

    def __int__(self, *args, **kwargs):
        super(ShipmentForm, self).__init__(*args, **kwargs)
        self.fields['issuance_date'] = JalaliDateField(label=('تاریخ صدور'),
                                                       widget=AdminJalaliDateWidget)

# class Bijak(forms.ModelForm):
#     class Meta:
#         model = Bijak
#         fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'
#         widgets = {
#             'issuance_date': forms.TextInput(attrs={
#                 'class': 'form-control persian-date-picker',
#                 'placeholder': 'تاریخ را انتخاب کنید'}),
#         }

# class Bijak(forms.ModelForm):
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
#         model = Bijak
#         fields = 'tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee'

# class Bijak(forms.ModelForm):
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
#         model = Bijak
#         fields = ['tracking_code', 'issuance_date', 'value', 'origin', 'destination', 'insurance', 'loading_fee']
#     widgets = {
#         'issuance_date': forms.TextInput(attrs={'class': 'persian-date-picker'}),
#     }
