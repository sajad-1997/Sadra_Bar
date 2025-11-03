from django.db import models
from django.utils import timezone
from django_jalali.db import models as jmodels
from persian_tools import digits
from django.conf import settings


class Customer(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام و نام خانوادگی فرستنده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه یا کد ملی", blank=True, null=True)
    postal = models.CharField(max_length=10, verbose_name="کد پستی", blank=True, null=True)
    phone = models.CharField(max_length=15, verbose_name="تلفن", blank=True, null=True)
    address = models.TextField(verbose_name="آدرس")
    phone2 = models.TextField(verbose_name="تلفن دوم", blank=True, null=True)
    caption = models.TextField(verbose_name="توضیحات", blank=True, null=True)

    def __str__(self):
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی راننده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="کد ملی راننده")
    father_name = models.CharField(max_length=50, verbose_name="نام پدر")
    birth_date = jmodels.jDateField(verbose_name="تاریخ تولد")
    residence = models.CharField(max_length=100, verbose_name="شهر محل سکونت")
    certificate = models.CharField(max_length=50, unique=True, verbose_name="شماره گواهینامه")
    certificate_date = jmodels.jDateField(verbose_name="تاریخ صدور گواهینامه")
    driver_smart_card = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="هوشمند راننده")
    phone = models.CharField(max_length=15, verbose_name="شماره تلفن راننده")
    phone2 = models.CharField(max_length=15, verbose_name="شماره تلفن دوم")
    address = models.TextField(verbose_name="آدرس محل سکونت")

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="انتخاب راننده")
    type = models.CharField(max_length=10, verbose_name="نوع وسیله")
    license_plate_two_digit = models.CharField(max_length=2, verbose_name="دو رقم پلاک")
    license_plate_alphabet = models.CharField(max_length=1, verbose_name="الفبای پلاک")
    license_plate_three_digit = models.CharField(max_length=3, verbose_name="سه رقم پلاک")
    license_plate_series = models.CharField(max_length=2, verbose_name="سری پلاک")
    vehicle_smart_card = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="هوشمند ناوگان")


    def __str__(self):
        return self.type


class Cargo(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام محموله")
    weight = models.CharField(max_length=5, verbose_name="وزن(کیلوگرم)/حجم(لیتر)")
    package_type = models.CharField(max_length=10, verbose_name="نوع بسته بندی", blank=True)
    number_of_packaging = models.CharField(max_length=3, verbose_name="تعداد بسته بندی", blank=True)
    origin = models.CharField(max_length=50, verbose_name="مبدا بارگیری")
    destination = models.CharField(max_length=50, verbose_name="مقصد تخلیه")

    def __str__(self):
        return self.name


class Caption(models.Model):
    name = models.CharField(max_length=100, verbose_name="عنوان")
    content = models.TextField(verbose_name="توضیحات")

    def __str__(self):
        return self.content[:50]


class Bijak(models.Model):
    tracking_code = models.CharField(max_length=10, unique=True, verbose_name="کد رهگیری")
    issuance_date = jmodels.jDateField(verbose_name="تاریخ صدور")
    value = models.CharField(max_length=100, verbose_name="ارزش محموله")
    insurance = models.CharField(max_length=100, verbose_name="مبلغ بیمه")
    loading_fee = models.CharField(max_length=100, verbose_name="هزینه خدمات")
    freight = models.CharField(max_length=100, verbose_name="مبلغ کرایه")
    total_fare = models.CharField(max_length=100, verbose_name="کل کرایه پرداختی در مقصد")

    sender = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='sender_bijaks')
    receiver = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='received_bijaks')
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, related_name='driverـbijaks')
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='vehicleـbijaks')
    cargo = models.ForeignKey('Cargo', on_delete=models.CASCADE, related_name='cargoـbijaks')

    status = models.CharField(max_length=30, choices=[
        ('draft', 'پیش‌نویس'),
        ('issued', 'صادر شده'),
        ('sent', 'ارسال شده'),
    ])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    default_description = 'هرگونه آب خوردگی و خیس شدن بار به مسئولیت راننده میباشد.'

    # انتخاب یک توضیح آماده از جدول Caption (تک انتخابی)
    selected_caption = models.ForeignKey(
        'Caption', on_delete=models.SET_NULL, null=True, blank=True, related_name='caption_bijaks'
    )

    # توضیح دستی کاربر
    custom_caption = models.TextField(blank=True, null=True)

    # توضیح نهایی که در بارنامه نمایش داده می‌شود (تجمیع شده)
    final_description = models.TextField(blank=True, null=True)

    @property
    def num_in_words(self):
        if self.total_fare is not None:
            print(self.total_fare)
            try:
                # حذف جداکننده‌ها (ویرگول و نقطه)
                value_str = str(self.total_fare).replace(",", "").replace(".", "")

                # تبدیل به عدد صحیح
                num = int(value_str)

                return digits.convert_to_word(num) + " ریال"  # تبدیل عدد به حروف فارسی
            except ValueError:
                return ""
        return ""

    def save(self, *args, **kwargs):
        # ساخت توضیح نهایی از سه بخش
        parts = [self.default_description]
        if self.selected_caption:
            parts.append(self.selected_caption.content)
        if self.custom_caption:
            parts.append(self.custom_caption)
        self.final_description = " | ".join(parts)

        # اگر کد رهگیری هنوز پر نشده
        if not self.tracking_code:
            last_bijak = Bijak.objects.order_by('-id').first()
            if last_bijak and last_bijak.tracking_code.isdigit():
                new_code = str(int(last_bijak.tracking_code) + 1).zfill(8)
            else:
                new_code = "00000001"
            self.tracking_code = new_code

        # تاریخ صدور فقط اگر خالی باشه
        if not self.issuance_date:
            self.issuance_date = timezone.now().date()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"بیجک {self.tracking_code} - {self.issuance_date}"
