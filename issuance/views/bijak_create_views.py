# 3️⃣ bijak_create_views.py (ایجاد بارنامه)

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from khayyam import JalaliDatetime

from .utils import persian_to_english_numbers, show_form_errors
from ..forms import ShipmentForm, CargoForm
from ..models import Customer, Driver, Vehicle, Caption


#
# @login_required
# @never_cache
# def create_new(request):
#     captions = Caption.objects.all().order_by('-id')
#
#     if request.method != 'POST':
#         return render(request, 'issuance/bijak/issuance_form.html', {
#             'shipment_form': ShipmentForm(prefix='shipment'),
#             'cargo_form': CargoForm(prefix='cargo'),
#             'captions': captions,
#         })
#
#     shipment_form = ShipmentForm(request.POST, prefix='shipment')
#     cargo_form = CargoForm(request.POST, prefix='cargo')
#
#     if not (shipment_form.is_valid() and cargo_form.is_valid()):
#         show_form_errors(request, shipment_form, "اطلاعات بارنامه")
#         show_form_errors(request, cargo_form, "اطلاعات محموله")
#         return render(request, 'issuance/bijak/issuance_form.html', {
#             'shipment_form': shipment_form,
#             'cargo_form': cargo_form,
#             'captions': captions,
#         })
#
#     try:
#         date_str = persian_to_english_numbers(shipment_form.cleaned_data['issuance_date'])
#         time_str = persian_to_english_numbers(shipment_form.cleaned_data['issuance_time'])
#         j_date = JalaliDatetime.strptime(date_str, "%Y/%m/%d")
#         h, m, s = map(int, time_str.split(':'))
#         issuance_datetime = datetime(j_date.year, j_date.month, j_date.day, h, m, s)
#     except Exception:
#         messages.error(request, "تاریخ یا ساعت معتبر نیست")
#         return redirect('issuance:crud:create_new')
#
#     sender = get_object_or_404(Customer, id=request.POST.get("sender"))
#     receiver = get_object_or_404(Customer, id=request.POST.get("receiver"))
#     driver = get_object_or_404(Driver, id=request.POST.get("driver"))
#     vehicle = Vehicle.objects.filter(driver=driver).order_by('-id').first()
#
#     with transaction.atomic():
#         cargo = cargo_form.save()
#         bijak = shipment_form.save(commit=False)
#         bijak.sender = sender
#         bijak.receiver = receiver
#         bijak.driver = driver
#         bijak.vehicle = vehicle
#         bijak.cargo = cargo
#         bijak.issuance_datetime = issuance_datetime
#         bijak.status = "draft"
#         bijak.approval_status = "pending"
#         bijak.save()
#
#     messages.success(request, "بارنامه با موفقیت ثبت شد")
#     return redirect('issuance:crud:preview', pk=bijak.id)
@login_required
@never_cache
def create_new(request):
    captions = Caption.objects.all().order_by('-id')

    if request.method != 'POST':
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': ShipmentForm(prefix='shipment'),
            'cargo_form': CargoForm(prefix='cargo'),
            'captions': captions,
            'user_role': getattr(request.user, 'role', 'staff'),
        })

    shipment_form = ShipmentForm(request.POST, prefix='shipment')
    cargo_form = CargoForm(request.POST, prefix='cargo')

    if not (shipment_form.is_valid() and cargo_form.is_valid()):
        show_form_errors(request, shipment_form, "اطلاعات بارنامه")
        show_form_errors(request, cargo_form, "اطلاعات محموله")
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': shipment_form,
            'cargo_form': cargo_form,
            'captions': captions,
            'user_role': getattr(request.user, 'role', 'staff'),
        })

    try:
        date_str = persian_to_english_numbers(shipment_form.cleaned_data['issuance_date'])
        time_str = persian_to_english_numbers(shipment_form.cleaned_data['issuance_time'])
        j_date = JalaliDatetime.strptime(date_str, "%Y/%m/%d")
        h, m, s = map(int, time_str.split(':'))
        issuance_datetime = datetime(j_date.year, j_date.month, j_date.day, h, m, s)
    except Exception:
        messages.error(request, "تاریخ یا ساعت معتبر نیست")
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': shipment_form,
            'cargo_form': cargo_form,
            'captions': captions,
            'user_role': getattr(request.user, 'role', 'staff'),
        })

    sender = get_object_or_404(Customer, id=request.POST.get("sender"))
    receiver = get_object_or_404(Customer, id=request.POST.get("receiver"))
    driver = get_object_or_404(Driver, id=request.POST.get("driver"))
    vehicle = Vehicle.objects.filter(driver=driver).order_by('-id').first()

    with transaction.atomic():
        cargo = cargo_form.save()
        bijak = shipment_form.save(commit=False)
        bijak.sender = sender
        bijak.receiver = receiver
        bijak.driver = driver
        bijak.vehicle = vehicle
        bijak.cargo = cargo
        bijak.issuance_datetime = issuance_datetime
        bijak.status = "draft"
        bijak.approval_status = "pending"  # همیشه pending برای کارمند
        bijak.save()

    messages.success(request, "بارنامه با موفقیت ثبت شد و برای تأیید مدیریت آماده است.")

    # کارمند بعد از ثبت → هدایت به صفحه داشبورد یا لیست بارنامه‌های خود
    if getattr(request.user, 'role', 'staff') == 'staff':
        return redirect('issuance:crud:pending')  # صفحه لیست بارنامه‌ها در انتظار تایید
    else:
        return redirect('issuance:crud:preview', pk=bijak.id)
