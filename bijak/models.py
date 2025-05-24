from django.db import models


class Sender(models.Model):
    name = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50, unique=True, )
    postal = models.CharField(max_length=10, )
    phone = models.CharField(max_length=11)
    address = models.TextField()

    def __str__(self):
        return self.name


class Receiver(models.Model):
    name = models.TextField()
    national_id = models.CharField(max_length=50, unique=True, )
    postal = models.CharField(max_length=10, )
    phone = models.CharField(max_length=11)
    address = models.TextField()

    def __str__(self):
        return self.name


class Driver(models.Model):
    name = models.TextField()
    national_id = models.CharField(max_length=50, unique=True, )
    brith_place = models.TextField()
    father_name = models.TextField()
    birth_date = models.DateField()
    phone = models.CharField(max_length=11)
    phone2 = models.CharField(max_length=11)
    address = models.TextField()
    certificate = models.CharField(max_length=50, unique=True, )

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    type = models.TextField()
    license_plate_three_digit = models.CharField(max_length=3)
    license_plate_alphabet = models.TextField(max_length=1)
    license_plate_two_digit = models.CharField(max_length=2)
    license_plate_series = models.CharField(max_length=2)


class Bijak(models.Model):
    tracking_code = models.CharField(max_length=10)
    date = models.DateTimeField()
    value = models.CharField(max_length=100)
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
