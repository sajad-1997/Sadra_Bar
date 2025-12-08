import jdatetime
from django import forms

from .models import Customer, Driver, Vehicle, Cargo, Caption, Bijak


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
    numeric_fields = ['national_id', 'phone', 'phone2', 'certificate']

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
    numeric_fields = ['license_plate_three_digit', 'license_plate_two_digit', 'license_plate_series']

    class Meta:
        model = Vehicle
        fields = '__all__'
        exclude = ['created_by', 'created_by_role', 'updated_by', 'updated_by_role']


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


class ShipmentForm(PersianNumberFormMixin, forms.ModelForm):
    class Meta:
        model = Bijak
        fields = ('issuance_date', 'issuance_time', 'total_fare', 'value', 'insurance', 'loading_fee', 'unloading_fee',
                  'scale_fee', 'freight',)  # فیلدهای مدلی
        exclude = ('tracking_code',)

    issuance_date = forms.CharField(
        required=True,
        label='تاریخ صدور بارنامه',
        widget=forms.TextInput(attrs={
            'class': 'date-picker form-control',
            # 'placeholder': 'تاریخ صدور بارنامه'
        })
    )

    issuance_time = forms.CharField(
        required=True,
        label='ساعت صدور بارنامه',
        widget=forms.TextInput(attrs={
            'class': 'time-picker form-control',
            # 'placeholder': 'ساعت صدور بارنامه'
        })
    )
    numeric_fields = ['tracking_code', 'value', 'total_fare', 'insurance',
                      'loading_fee', 'unloading_fee', 'scale_fee', 'freight']

    # # فیلد چندتایی توضیحات
    # captions = forms.ModelMultipleChoiceField(
    #     queryset=Caption.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label="انتخاب توضیحات"
    # )

    class Meta:
        model = Bijak
        fields = ('issuance_date', 'issuance_time', 'total_fare', 'value', 'insurance', 'loading_fee', 'unloading_fee',
                  'scale_fee', 'freight',)  # فیلدهای مدلی
        exclude = ('tracking_code',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # مقداردهی اولیه فیلدهای نمایشی
        if self.instance and self.instance.pk:
            self.fields['tracking_code_display'].initial = getattr(self.instance, 'tracking_code', '')
            issuance = getattr(self.instance, 'issuance_date', '')
            self.fields['issuance_date_display'].initial = str(issuance)

        # تاریخ صدور جلالی
        # self.fields['issuance_date'] = JalaliDateField(
        #     label="تاریخ صدور",
        #     widget=AdminJalaliDateWidget
        # )

        # افزودن کلاس مخصوص به فیلدهای عددی
        for field_name in self.numeric_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'numeric-field'})

    class Media:
        js = ('js/shipment_form.js',)  # فایل جاوااسکریپت که رفتار محاسباتی را انجام می‌دهد
#
# def __int__(self, *args, **kwargs):
#     super(ShipmentForm, self).__init__(*args, **kwrgs)
#     self.fields['issuance_date'] = JalaliDateField(label=('تاریخ صدور'),
#                                                    widget=AdminJalaliDateWidget)
