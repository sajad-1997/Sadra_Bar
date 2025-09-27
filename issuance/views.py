from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomerForm, DriverForm, VehicleForm, CargoForm, CaptionForm, ShipmentForm
from .models import Customer, Driver, Vehicle, Cargo, Caption, Bijak


def create_new(request):
    """ایجاد بیجک جدید (بارنامه + محموله)"""

    if request.method == 'POST':
        # شناسه‌ها
        sender_id = request.POST.get("sender")
        receiver_id = request.POST.get("receiver")
        driver_id = request.POST.get("driver")
        caption_id = request.POST.get("captions")  # ✅ گرفتن توضیح انتخابی

        # فرم‌ها
        cargo_form = CargoForm(request.POST, prefix='cargo')
        shipment_form = ShipmentForm(request.POST, prefix='shipment')

        if cargo_form.is_valid() and shipment_form.is_valid():
            try:
                sender = get_object_or_404(Customer, id=sender_id)
                receiver = get_object_or_404(Customer, id=receiver_id)
                driver = get_object_or_404(Driver, id=driver_id)
            except Exception:
                messages.error(request, "فرستنده، گیرنده یا راننده معتبر نیستند.")
                return redirect('create_new')

            vehicle = Vehicle.objects.filter(driver_id=driver.id).order_by('-id').first()

            cargo = cargo_form.save()
            shipment = shipment_form.save(commit=False)
            shipment.sender = sender
            shipment.receiver = receiver
            shipment.driver = driver
            shipment.cargo = cargo

            if vehicle:
                shipment.vehicle = vehicle
                # ذخیره انتخاب‌های چندتایی توضیحات
            captions = shipment_form.cleaned_data.get('captions')
            if captions:
                shipment.captions.set(captions)  # اگر فیلد ManyToMany هست
                # اگر میخوای فقط یک توضیح اصلی باشه، می‌تونی shipment.explanation = captions.first()

            shipment.save()

            messages.success(request, "بیجک با موفقیت ثبت شد.")
            return redirect('success')

    else:
        cargo_form = CargoForm(prefix='cargo')
        shipment_form = ShipmentForm(prefix='shipment')

    return render(request, 'bijak/issuance_form.html', {
        'cargo_form': cargo_form,
        'shipment_form': shipment_form,
    })


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
            Q(captions__name__icontains=query)
        )

    return render(request, 'bijak/bijak_search.html', {
        'shipments': shipments,
        'query': query
    })


def search_customer(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    # جستجو فقط بر اساس همون مقدار وارد شده (بدون حذف فاصله‌ها)
    customer = Customer.objects.filter(
        Q(name__icontains=query)
    )[:10]

    results = []
    for s in customer:
        results.append({
            "id": s.id,
            "name": s.name,
            "phone": s.phone,
            "address": s.address,
            "national_id": s.national_id,
            "postal": s.postal,
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
                name=name, national_id=national_id, postal=postal,
                phone=phone, address=address,
            )

        return JsonResponse({"success": True, "id": customer.id})

    return JsonResponse({"success": False, "error": "Invalid request"})


def search_driver(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    drivers = Driver.objects.filter(
        Q(name__icontains=query)
    )[:10]

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
    return render(request, 'bijak/barnameh2.html')


# preview pages defs
def print_page(request, pk):
    shipment = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo'
    ).prefetch_related(
        'captions'
    ).get(pk=pk)
    return render(request, 'secondary/print.html', {'shipment': shipment})


def preview_page(request, pk):
    bijak = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo'
    ).prefetch_related(
        'captions'
    ).get(pk=pk)
    return render(request, 'secondary/preview.html', {'bijak': bijak})


# add date defs
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


def bijak_last_view(request):
    bijak = Bijak.objects.last()  # آخرین رکورد جدول
    return render(request, "bijak/barnameh2.html", {"bijak": bijak})


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


def edit_bijak(request):
    return render(request, 'secondary/print.html')
