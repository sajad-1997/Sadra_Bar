from django.db import models
import django_jalali.db.models as jmodels


class Sender(models.Model):
    name = models.CharField(max_length=20, verbose_name="نام و نام خانوادگی فرستنده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه یا کد ملی", blank=True, null=True)
    postal = models.CharField(max_length=10, verbose_name="کد پستی", blank=True, null=True)
    phone = models.CharField(max_length=11, verbose_name="تلفن", blank=True, null=True)
    address = models.TextField(verbose_name="آدرس")

    def __str__(self):
        return self.name


class Receiver(models.Model):
    name = models.CharField(max_length=20, verbose_name="نام و نام خانوادگی گیرنده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه یا کد ملی", blank=True)
    postal = models.CharField(max_length=10, verbose_name="کد پستی", blank=True)
    phone = models.CharField(max_length=11, verbose_name="تلفن", blank=True)
    address = models.TextField(verbose_name="آدرس")

    def __str__(self):
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=20, verbose_name="نام و نام خانوادگی راننده")
    national_id = models.CharField(max_length=50, unique=True, verbose_name="کد ملی راننده")
    brith_place = models.CharField(max_length=10, verbose_name="محل تولد")
    father_name = models.CharField(max_length=10, verbose_name="نام پدر")
    birth_date = models.DateField(verbose_name="تاریخ تولد")
    phone = models.CharField(max_length=11, verbose_name="شماره تلفن راننده")
    phone2 = models.CharField(max_length=11, verbose_name="شماره تلفن دوم")
    address = models.TextField(verbose_name="آدرس محل سکونت")
    certificate = models.CharField(max_length=50, unique=True, verbose_name="شماره گواهینامه")
    certificate_date = models.DateField(verbose_name="تاریخ صدور گواهینامه")

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="انتخاب راننده")
    type = models.CharField(max_length=10, verbose_name="نوع وسیله")
    license_plate_three_digit = models.IntegerField(max_length=3, verbose_name="سه رقم پلاک")
    license_plate_alphabet = models.CharField(max_length=1, verbose_name="الفبای پلاک")
    license_plate_two_digit = models.IntegerField(max_length=2, verbose_name="دو رقم پلاک")
    license_plate_series = models.CharField(max_length=2, verbose_name="سری پلاک")

    def __str__(self):
        return self.type


class Cargo(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام محموله")
    weight = models.IntegerField(max_length=5, verbose_name="وزن(کیلوگرم)/حجم(لیتر)", blank=True)
    package_type = models.CharField(max_length=10, verbose_name="نوع بسته بندی", blank=True)
    number_of_packaging = models.IntegerField(max_length=3, verbose_name="تعداد بسته بندی", blank=True)

    def __str__(self):
        return self.name


class BijakForm(models.Model):
    tracking_code = models.CharField(max_length=10, verbose_name="کد رهگیری")
    issuance_date = jmodels.jDateField(verbose_name="تاریخ صدور")
    value = models.CharField(max_length=100, verbose_name="ارزش محموله", blank=True)
    origin = models.CharField(max_length=50, verbose_name="مبدا بارگیری", blank=True)
    destination = models.CharField(max_length=50, verbose_name="مقصد تخلیه")
    insurance = models.CharField(max_length=100, verbose_name="مبلغ بیمه")
    loading_fee = models.CharField(max_length=10, verbose_name="هزینه خدمات", blank=True)
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    def __str__(self):
        return self.issuance_date
