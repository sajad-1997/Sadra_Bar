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
    numeric_fields = ['weight', 'number_of_packaging', ]

    class Meta:
        model = Cargo
        fields = '__all__'


class CaptionForm(forms.ModelForm):
    class Meta:
        model = Caption
        fields = '__all__'

    captions = forms.ModelMultipleChoiceField(
        queryset=Caption.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="انتخاب توضیحات آماده"
    )
    custom_explanation = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="توضیحات دستی"
    )


class ShipmentForm(PersianNumberFormMixin, forms.ModelForm):
    numeric_fields = ['tracking_code', 'issuance_date', 'value', 'total_fare', 'insurance', 'loading_fee', 'freight']

    # فیلدهای نمایشی
    tracking_code_display = forms.CharField(label="کد رهگیری", required=False, disabled=True)
    issuance_date_display = forms.CharField(label="تاریخ صدور", required=False, disabled=True)

    # فیلد چندتایی توضیحات
    captions = forms.ModelMultipleChoiceField(
        queryset=Caption.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="انتخاب توضیحات"
    )

    class Meta:
        model = Bijak
        exclude = ('tracking_code', 'issuance_date')
        fields = ('value', 'total_fare', 'insurance', 'loading_fee', 'freight', )  # فیلدهای مدلی

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
#     super(ShipmentForm, self).__init__(*args, **kwargs)
#     self.fields['issuance_date'] = JalaliDateField(label=('تاریخ صدور'),
#                                                    widget=AdminJalaliDateWidget)
