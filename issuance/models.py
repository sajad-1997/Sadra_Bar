from django.db import models
from django_jalali.db import models as jmodels


class Customer(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام و نام خانوادگی فرستنده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه یا کد ملی", blank=True, null=True)
    postal = models.CharField(max_length=10, verbose_name="کد پستی", blank=True, null=True)
    phone = models.CharField(max_length=15, verbose_name="تلفن", blank=True, null=True)
    address = models.TextField(verbose_name="آدرس")
    phone2 = models.TextField(verbose_name="تلفن۲", blank=True, null=True)
    caption = models.TextField(verbose_name="توضیحات", blank=True, null=True)

    def __str__(self):
        return self.name


# class Customer(models.Model):
#     name = models.CharField(max_length=50, verbose_name="نام و نام خانوادگی گیرنده")
#     national_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه یا کد ملی", blank=True)
#     postal = models.CharField(max_length=10, verbose_name="کد پستی", blank=True)
#     phone = models.CharField(max_length=11, verbose_name="تلفن", blank=True)
#     address = models.TextField(verbose_name="آدرس", blank=True, null=True)
#
#     def __str__(self):
#         return self.name


class Driver(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی راننده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="کد ملی راننده")
    residence = models.CharField(max_length=100, verbose_name="شهر محل سکونت")
    father_name = models.CharField(max_length=50, verbose_name="نام پدر")
    birth_date = jmodels.jDateField(verbose_name="تاریخ تولد")
    certificate_date = jmodels.jDateField(verbose_name="تاریخ صدور گواهینامه")
    certificate = models.CharField(max_length=50, unique=True, verbose_name="شماره گواهینامه")
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


class Bijak(models.Model):
    tracking_code = models.CharField(max_length=10, verbose_name="کد رهگیری")
    issuance_date = jmodels.jDateField(verbose_name="تاریخ صدور")
    value = models.CharField(max_length=100, verbose_name="ارزش محموله", blank=True)
    insurance = models.CharField(max_length=100, verbose_name="مبلغ بیمه")
    loading_fee = models.CharField(max_length=10, verbose_name="هزینه خدمات", blank=True)
    freight = models.CharField(max_length=11, verbose_name="کرایه حمل")
    sender = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='فرستنده')
    receiver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='گیرنده')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='راننده')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='خودرو')
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='محموله')

    def __str__(self):
        return self.tracking_code
