from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import qrcode
from io import BytesIO
from django.http import HttpResponse
from .forms import CustomerForm, DriverForm, VehicleForm, CargoForm, CaptionForm, ShipmentForm
from .models import Customer, Driver, Vehicle, Caption, Bijak


# from .utils import num_to_word_rial


# -----------------------
# بیجک جدید (ثبت)
# -----------------------
def create_new(request):
    """ایجاد بیجک جدید (بارنامه + محموله)"""

    if request.method == 'POST':
        action = request.POST.get('action')  # دکمه ثبت یا چاپ
        sender_id = request.POST.get("sender")
        receiver_id = request.POST.get("receiver")
        driver_id = request.POST.get("driver")
        selected_caption_id = request.POST.get("selected_caption")  # توضیح انتخابی
        manual_text = request.POST.get("manual_description", "").strip()  # توضیح دستی

        shipment_form = ShipmentForm(request.POST, prefix='shipment')
        cargo_form = CargoForm(request.POST, prefix='cargo')

        if shipment_form.is_valid() and cargo_form.is_valid():
            # دریافت اشیاء قبل از atomic
            try:
                sender = get_object_or_404(Customer, id=sender_id)
                receiver = get_object_or_404(Customer, id=receiver_id)
                driver = get_object_or_404(Driver, id=driver_id)
            except Exception:
                messages.error(request, "فرستنده، گیرنده یا راننده معتبر نیستند.")
                return redirect('create_new')

            vehicle = Vehicle.objects.filter(driver_id=driver.id).order_by('-id').first()

            with transaction.atomic():
                # ذخیره محموله
                cargo = cargo_form.save()

                # ایجاد بیجک
                bijak = shipment_form.save(commit=False)
                bijak.sender = sender
                bijak.receiver = receiver
                bijak.driver = driver
                bijak.vehicle = vehicle
                bijak.cargo = cargo

                # توضیح انتخابی
                if selected_caption_id:
                    try:
                        selected_caption = Caption.objects.get(id=selected_caption_id)
                        bijak.selected_caption = selected_caption
                    except Caption.DoesNotExist:
                        pass

                # توضیح دستی
                if manual_text:
                    # ذخیره در جدول Caption برای استفاده احتمالی آینده
                    Caption.objects.create(content=manual_text)
                    bijak.custom_caption = manual_text

                # ذخیره بیجک
                bijak.save()

            # هدایت بعد از ذخیره
            if action == 'print':
                return redirect('print', pk=bijak.pk)

            messages.success(request, "بیجک با موفقیت ثبت شد.")
            return redirect('preview', pk=bijak.pk)

        else:
            messages.error(request, "خطا در اعتبارسنجی فرم‌ها. لطفاً دوباره بررسی کنید.")


    else:
        shipment_form = ShipmentForm(prefix='shipment')
        cargo_form = CargoForm(prefix='cargo')

    # پاس دادن تمام توضیحات موجود به قالب
    captions = Caption.objects.all().order_by('-id')

    return render(request, 'bijak/issuance_form.html', {
        'shipment_form': shipment_form,
        'cargo_form': cargo_form,
        'captions': captions,
    })


def to_words_view(request):
    num = request.GET.get("num", "0")
    words = num_to_word_rial(num)
    return JsonResponse({"words": words})


# -----------------------
# جستجوی بیجک
# -----------------------
def search_shipment(request):
    query = request.GET.get('q', '').strip()
    shipments = Bijak.objects.all()

    if query:
        shipments = shipments.filter(
            Q(sender__name__icontains=query) |
            Q(receiver__name__icontains=query) |
            Q(driver__name__icontains=query) |
            Q(vehicle__license_plate_two_digit__icontains=query) |
            Q(vehicle__license_plate_three_digit__icontains=query) |
            Q(vehicle__license_plate_alphabet__icontains=query) |
            Q(vehicle__license_plate_series__icontains=query) |
            Q(cargo__name__icontains=query) |
            Q(selected_caption__content__icontains=query)  # تغییر به selected_caption
        )

    return render(request, 'bijak/bijak_search.html', {
        'shipments': shipments,
        'query': query
    })


# -----------------------
# سایر جستجوها (مشتری، راننده، وسیله)
# -----------------------
def search_customer(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    # جستجو فقط بر اساس همون مقدار وارد شده (بدون حذف فاصله‌ها)
    customers = Customer.objects.filter(
        Q(name__icontains=query)
    )[:5]

    results = []
    for c in customers:
        results.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "address": c.address,
            "national_id": c.national_id,
            "postal": c.postal,
        })

    return JsonResponse({"results": results})


@csrf_exempt
def save_customer(request):
    if request.method == "POST":
        customer_id = request.POST.get("id")
        name = request.POST.get("name")
        national_id = request.POST.get("national_id")
        postal = request.POST.get("postal")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if customer_id:  # اگر رکورد وجود داشت → ویرایش
            try:
                customer = Customer.objects.get(id=customer_id)
                customer.name = name
                customer.national_id = national_id
                customer.postal = postal
                customer.phone = phone
                customer.address = address
                customer.save()
            except Customer.DoesNotExist:
                return JsonResponse({"success": False, "error": "مشتری یافت نشد"})
        else:  # ایجاد رکورد جدید
            customer = Customer.objects.create(
                name=name,
                national_id=national_id,
                postal=postal,
                phone=phone,
                address=address,
            )

        return JsonResponse({"success": True, "id": customer.id})

    return JsonResponse({"success": False, "error": "Invalid request"})


def duplicate_customer(request):
    if request.method == "POST":
        try:
            # رکورد جدید بساز
            new_customer = Customer.objects.create(
                name=request.POST.get("name"),
                national_id=request.POST.get("national_id"),
                postal=request.POST.get("postal"),
                phone=request.POST.get("phone"),
                address=request.POST.get("address"),
            )

            return JsonResponse({"success": True, "new_id": new_customer.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "درخواست نامعتبر"})


def search_driver(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    drivers = Driver.objects.filter(
        Q(name__icontains=query)
    )[:5]

    results = []
    for d in drivers:
        try:
            vehicle = Vehicle.objects.get(driver=d)
            plate = [
                vehicle.license_plate_two_digit,
                vehicle.license_plate_alphabet,
                vehicle.license_plate_three_digit,
                vehicle.license_plate_series,
            ]
        except Vehicle.DoesNotExist:
            plate = ""

        results.append({
            "id": d.id,
            "name": d.name,
            "national_id": d.national_id,
            "residence": d.residence,
            "father_name": d.father_name,
            "birth_date": d.birth_date.isoformat() if d.birth_date else "",
            "certificate_date": d.certificate_date.isoformat() if d.certificate_date else "",
            "certificate": d.certificate,
            "phone": d.phone,
            "phone2": d.phone2,
            "address": d.address,
            "plate_number": plate,
        })
    return JsonResponse({"results": results})


@csrf_exempt
def save_driver(request):
    if request.method == "POST":
        driver_id = request.POST.get("id")
        name = request.POST.get("name")
        national_id = request.POST.get("national_id")
        residence = request.POST.get("residence")
        father_name = request.POST.get("father_name")
        birth_date = request.POST.get("birth_date") or None
        certificate_date = request.POST.get("certificate_date") or None
        certificate = request.POST.get("certificate")
        phone = request.POST.get("phone")
        phone2 = request.POST.get("phone2")
        address = request.POST.get("address")

        if driver_id:  # ویرایش
            try:
                driver = Driver.objects.get(id=driver_id)
                driver.name = name
                driver.national_id = national_id
                driver.residence = residence
                driver.father_name = father_name
                driver.birth_date = birth_date
                driver.certificate_date = certificate_date
                driver.certificate = certificate
                driver.phone = phone
                driver.phone2 = phone2
                driver.address = address
                driver.save()
            except Driver.DoesNotExist:
                return JsonResponse({"success": False, "error": "راننده یافت نشد"})
        else:  # ایجاد جدید
            driver = Driver.objects.create(
                name=name, national_id=national_id, residence=residence,
                father_name=father_name, birth_date=birth_date,
                certificate_date=certificate_date, certificate=certificate,
                phone=phone, phone2=phone2, address=address,
            )

        return JsonResponse({"success": True, "id": driver.id})

    return JsonResponse({"success": False, "error": "Invalid request"})


#
# def search_driver(request):
#     q = request.GET.get("q", "")
#     drivers = Driver.objects.filter(name__icontains=q)[:10]
#
#     results = []
#     for d in drivers:
#         try:
#             vehicle = Vehicle.objects.get(driver=d)
#             plate = vehicle.license_plate_three_digit
#         except Vehicle.DoesNotExist:
#             plate = ""
#
#         results.append({
#             "id": d.id,
#             "name": d.name,
#             "phone": d.phone,
#             "plate_number": plate  # 👈 پلاک هم اضافه شد
#         })
#     return JsonResponse({"results": results})
#

def search_vehicle(request):
    q = request.GET.get("q", "")
    results = Vehicle.objects.filter(plate__icontains=q)[:10]
    return JsonResponse({"results": list(results.values("id", "plate"))})


# page render defs
def success_page(request):
    return render(request, 'secondary/success.html')


def search_page(request):
    return render(request, 'bijak/final_bijak.html')


# -----------------------
# پیش‌نمایش و چاپ
# -----------------------
def print_page(request, pk):
    shipment = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo', 'selected_caption'
    ).get(pk=pk)
    return render(request, 'secondary/print.html', {'shipment': shipment})


def preview_page(request, pk):
    bijak = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo', 'selected_caption'
    ).get(pk=pk)
    return render(request, 'secondary/preview.html', {'bijak': bijak})


def bijak_last_view(request, pk):
    # bijak = Bijak.objects.last()  # آخرین رکورد جدول
    if pk:
        bijak = get_object_or_404(Bijak, pk=pk)
    else:
        bijak = Bijak.objects.last()
    return render(request, "bijak/final_bijak.html", {"bijak": bijak})


# -----------------------
# افزودن مشتری، راننده، وسیله و توضیح
# -----------------------
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_new')  # بازگشت به فرم بارنامه
    else:
        form = CustomerForm()
    return render(request, 'add/add_customer.html', {"form": form})


def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_new')  # بازگشت به فرم بارنامه
    else:
        form = DriverForm()
    return render(request, 'add/add_driver.html', {"form": form})


def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            # vehicle = form.save()
            # return redirect("show_plate", vehicle_id=vehicle.id)
            return redirect('create_new')  # بازگشت به فرم بارنامه
    else:
        form = VehicleForm()
    return render(request, "add/add_vehicle.html", {"form": form})


def get_vehicle_by_driver(request):
    driver_id = request.GET.get("driver_id")
    try:
        vehicle = Vehicle.objects.get(driver_id=driver_id)
        data = {
            "two_digit": vehicle.license_plate_two_digit,
            "alphabet": vehicle.license_plate_alphabet,
            "three_digit": vehicle.license_plate_three_digit,
            "series": vehicle.license_plate_series,
        }
        return JsonResponse({"success": True, "vehicle": data})
    except Vehicle.DoesNotExist:
        return JsonResponse({"success": False, "error": "وسیله‌ای برای این راننده پیدا نشد"})


def add_caption(request):
    if request.method == "POST":
        form = CaptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ توضیحات با موفقیت ذخیره شد.")
            return redirect("create_new")
    else:
        form = CaptionForm()

    return render(request, 'add/add_caption.html', {"form": form})


def save_bijak(request):
    if request.method == "POST":
        bijak = Bijak.objects.last()
        if bijak:
            bijak.tracking_code = request.POST.get("tracking_code")
            bijak.issuance_date = request.POST.get("issuance_date")
            bijak.value = request.POST.get("value")
            bijak.insurance = request.POST.get("insurance")
            bijak.loading_fee = request.POST.get("loading_fee")
            bijak.freight = request.POST.get("freight")
            bijak.caption = request.POST.get("caption")
            bijak.sender = request.POST.get("sender")
            bijak.receiver = request.POST.get("receiver")
            bijak.driver = request.POST.get("driver")
            bijak.vehicle = request.POST.get("vehicle")
            bijak.cargo = request.POST.get("cargo")
            bijak.save()
        return HttpResponseRedirect(reverse("bijak_last_view"))


#
# def edit_sender(request):
#     sender = None
#
#     if request.method == 'POST':
#         name = request.POST.get('name')  # نام وارد شده توسط کاربر
#         sender = Customer.objects.filter(name__iexact=name).first()
#
#         if sender:
#             # اگر فرستنده پیدا شد → فرم پر بشه با اطلاعاتش
#             form = SenderForm(request.POST, instance=sender)
#         else:
#             # اگر فرستنده جدید بود → فرم ایجاد رکورد جدید
#             form = SenderForm(request.POST)
#
#         if form.is_valid():
#             form.save()
#             return redirect('create_new')
#
#     else:
#         # GET request → نمایش فرم خالی
#         form = SenderForm()
#
#     return render(request, 'edit/edit_customer.html', {"form": form})
#


def edit_customer(request):
    return render(request, 'edit/edit_customer.html')


def edit_driver(request):
    return render(request, 'edit/edit_driver.html')


def edit_vehicle(request):
    return render(request, 'edit/edit_vehicle.html')


def edit_cargo(request):
    return render(request, 'edit/edit_cargo.html')


# -----------------------
# ویرایش بارنامه صادر شده
# -----------------------
def edit_bijak(request):
    bijak = get_object_or_404(Bijak)

    if request.method == 'POST':
        bijak_form = ShipmentForm(request.POST, instance=bijak)
        sender_form = CustomerForm(request.POST, prefix='sender', instance=bijak.sender)
        receiver_form = CustomerForm(request.POST, prefix='receiver', instance=bijak.receiver)
        driver_form = DriverForm(request.POST, prefix='driver', instance=bijak.driver)
        vehicle_form = VehicleForm(request.POST, instance=bijak.vehicle)
        cargo_form = CargoForm(request.POST, instance=bijak.cargo)

        if all([
            bijak_form.is_valid(),
            sender_form.is_valid(),
            receiver_form.is_valid(),
            driver_form.is_valid(),
            vehicle_form.is_valid(),
            cargo_form.is_valid()
        ]):
            bijak_form.save()
            sender_form.save()
            receiver_form.save()
            driver_form.save()
            vehicle_form.save()
            cargo_form.save()

            messages.success(request, "بیجک با موفقیت ویرایش شد ✅")
            return redirect('preview', pk=bijak.pk)  # صفحه نمایش نهایی
    else:
        bijak_form = ShipmentForm(instance=bijak)
        sender_form = CustomerForm(prefix='sender', instance=bijak.sender)
        receiver_form = CustomerForm(prefix='receiver', instance=bijak.receiver)
        driver_form = DriverForm(prefix='driver', instance=bijak.driver)
        vehicle_form = VehicleForm(instance=bijak.vehicle)
        cargo_form = CargoForm(instance=bijak.cargo)

    return render(request, 'edit/edit_bijak.html', {
        'bijak_form': bijak_form,
        'sender_form': sender_form,
        'receiver_form': receiver_form,
        'driver_form': driver_form,
        'vehicle_form': vehicle_form,
        'cargo_form': cargo_form,
        'bijak': bijak,
    })


def bijak_qr(request, pk):
    bijak = get_object_or_404(Bijak, pk=pk)

    # لینک مقصد: صفحه چاپ بارنامه
    url = request.build_absolute_uri(f"/bijak/{pk}/print/")

    # تولید QR
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")
