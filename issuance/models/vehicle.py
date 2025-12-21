from django.db import models

from .base import UserTrackingModel
from .driver import Driver


class Vehicle(UserTrackingModel):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="انتخاب راننده")
    type = models.CharField(
        max_length=50,
        verbose_name='نوع ناوگان',
        choices=[
            ('peykan', 'وانت پیکان'),
            ('neysan', 'وانت نیسان'),
            ('arisan', 'وانت آریسان'),
            ('zamyad', 'وانت زامیاد'),
            ('Bari 20T', 'باری چوبی ۱۷ تا ۲۰ تن'),
        ])
    # room_model = models.CharField(
    #     max_length=50,
    #     verbose_name='مدل اتاق ناوگان',
    #     choices=[
    #         ('Normal', 'معمولی'),
    #         ('flat_floor', 'کف صاف'),
    #         ('sofa_floor', 'کف مبلی'),
    #     ],
    #     default='Normal')
    # Animal_feed_license = models.CharField(
    #     max_length=6,
    #     null=True,
    #     blank=True,
    #     verbose_name='مجوز حمل خوراک دام',
    #     choices=[
    #         ('No', 'ندارد'),
    #         ('Yes', 'دارد'),
    #     ], default='No')
    # veterinary_code = models.CharField(max_length=7, blank=True, null=True, verbose_name="کد دامپزشکی")
    license_plate_two_digit = models.CharField(max_length=2, verbose_name="دو رقم پلاک")
    license_plate_alphabet = models.CharField(max_length=1, verbose_name="الفبای پلاک")
    license_plate_three_digit = models.CharField(max_length=3, verbose_name="سه رقم پلاک")
    license_plate_series = models.CharField(max_length=2, verbose_name="سری پلاک")
    vehicle_smart_card = models.CharField(max_length=50, unique=True, blank=True, null=True,
                                          verbose_name="هوشمند ناوگان")

    def __str__(self):
        return self.type
