from datetime import datetime

import jdatetime
from django import forms
from khayyam import JalaliDatetime

from .models import Customer, Driver, Vehicle, Cargo, Caption, Bijak


# from .mixins import PersianNumberFormMixin


# 🔹 تابع تبدیل اعداد فارسی به انگلیسی
def persian_to_english_numbers(value: str) -> str:
    if not value:  # None یا ''
        return ''
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    trans_table = str.maketrans(persian_digits, english_digits)
    return str(value).translate(str.maketrans(persian_digits, english_digits))


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


class CustomerForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['national_id', 'postal', 'phone']

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['created_by', 'created_by_role', 'updated_by', 'updated_by_role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # مشخص کردن فیلدهای الزامی در فرم
        self.fields['name'].required = True
        # self.fields['national_id'].required = True
        # self.fields['postal'].required = True
        self.fields['address'].required = True

    # اعتبارسنجی فیلدهایی که باید کامل شوند
    def clean(self):
        cleaned_data = super().clean()

        required_fields = ['name', 'address']
        errors = {}

        for f in required_fields:
            if not cleaned_data.get(f):
                errors[f] = "پر کردن این فیلد الزامی است."

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class DriverForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['national_id', 'birth_date', 'certificate', 'certificate_date', 'phone', 'phone2', ]

    # اضافه کردن فیلدهای تاریخ با placeholder و کلاس date-picker
    birth_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'date-picker form-control',
            'placeholder': 'تاریخ تولد'
        })
    )

    certificate_date = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'date-picker form-control',
            'placeholder': 'تاریخ صدور گواهینامه'
        })
    )

    class Meta:
        model = Driver
        fields = '__all__'
        exclude = ['created_by', 'created_by_role', 'updated_by', 'updated_by_role']

    def clean_birth_date(self):
        data = self.cleaned_data['birth_date']
        if isinstance(data, str) and data:
            return persian_to_gregorian(data)  # تبدیل Jalali به میلادی
        return data

    def clean_certificate_date(self):
        data = self.cleaned_data['certificate_date']
        if isinstance(data, str) and data:
            return persian_to_gregorian(data)
        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # افزودن کلاس numeric-field به فیلدهای عددی
        for field_name in self.numeric_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'numeric-field'})


class VehicleForm(PersianNumberFormMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'driver',
            'type',
            # 'room_model',
            # 'Animal_feed_license',
            # 'veterinary_code',
            'license_plate_two_digit',
            'license_plate_alphabet',
            'license_plate_three_digit',
            'license_plate_series',
            'vehicle_smart_card',
        ]
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            # 'room_model': forms.Select(attrs={'class': 'form-control'}),
            # 'Animal_feed_license': forms.Select(attrs={'class': 'form-control', 'id': 'id_animal_license'}),
            # 'veterinary_code': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'id': 'id_veterinary_code',
            #     'maxlength': '7',
            #     'inputmode': 'numeric',
            #     'pattern': '[0-9]*',
            #     'disabled': 'disabled'
            # }),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     license_status = cleaned_data.get('Animal_feed_license')
    #     vet_code = cleaned_data.get('veterinary_code')
    #
    #     if license_status == 'Yes' and not vet_code:
    #         self.add_error(
    #             'veterinary_code',
    #             'در صورت داشتن مجوز خوراک دام، وارد کردن کد دامپزشکی الزامی است.'
    #         )
    #
    #     if license_status == 'No':
    #         cleaned_data['veterinary_code'] = ''
    #
    #     return cleaned_data


class CargoForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['weight', 'number_of_packaging', ]

    class Meta:
        model = Cargo
        fields = '__all__'
        exclude = ['created_by', 'created_by_role', 'updated_by', 'updated_by_role']


class CaptionForm(forms.ModelForm):
    class Meta:
        model = Caption
        fields = '__all__'

    captions = forms.ModelMultipleChoiceField(
        queryset=Caption.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        # label="انتخاب توضیحات آماده"
    )
    custom_explanation = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="توضیحات دستی"
    )


class ShipmentForm(forms.ModelForm):
    # فیلدهای date/time جداگانه برای انتخاب کاربر
    issuance_date = forms.CharField(
        label="تاریخ صدور بارنامه",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'date-picker form-control',
            'placeholder': '۱۴۰۳/۰۱/۲۰'
        })
    )

    issuance_time = forms.CharField(
        label="ساعت صدور بارنامه",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'time-picker form-control',
            'placeholder': '۱۵:۳۰:۰۰'
        })
    )

    class Meta:
        model = Bijak
        fields = ('total_fare', 'value', 'insurance',
                  'loading_fee', 'unloading_fee', 'scale_fee', 'freight')
        exclude = ('tracking_code', 'issuance_date', 'issuance_time', )

    def clean(self):
        cleaned_data = super().clean()

        date_str = persian_to_english_numbers(cleaned_data.get('issuance_date'))
        time_str = persian_to_english_numbers(cleaned_data.get('issuance_time'))

        try:
            j_date = JalaliDatetime.strptime(date_str, "%Y/%m/%d")
            j_time = JalaliDatetime.strptime(time_str, "%H:%M:%S")

            issuance_datetime = JalaliDatetime(
                j_date.year,
                j_date.month,
                j_date.day,
                j_time.hour,
                j_time.minute,
                j_time.second
            ).todatetime()

            cleaned_data['issuance_datetime'] = issuance_datetime

        except Exception:
            raise forms.ValidationError(
                "تاریخ یا ساعت وارد شده معتبر نیست."
            )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # # مقداردهی اولیه تاریخ و ساعت برای ویرایش
        # if self.instance and self.instance.pk and self.instance.issuance_datetime:
        #     self.fields['issuance_date_input'].initial = jdatetime.date.fromgregorian(
        #         date=self.instance.issuance_datetime
        #     ).strftime('%Y/%m/%d')
        #     self.fields['issuance_time_input'].initial = self.instance.issuance_time.strftime('%H:%M')
