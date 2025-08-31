from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from .models import Receiver, Sender, Driver, Vehicle, Bijak
from .forms import SenderForm, ReceiverForm, DriverForm, VehicleForm, CargoForm, ShipmentForm
from django.db.models import Q


def create_new(request):
    if request.method == 'POST':
        sender_id = request.POST.get("sender")
        receiver_id = request.POST.get("receiver")
        driver_id = request.POST.get("driver")

        cargo_form = CargoForm(request.POST, prefix='cargo')
        shipment_form = ShipmentForm(request.POST, prefix='shipment')

        if cargo_form.is_valid() and shipment_form.is_valid():
            # احراز موجودیت فرستنده/گیرنده/راننده
            try:
                sender = get_object_or_404(Sender, id=sender_id)
                receiver = get_object_or_404(Receiver, id=receiver_id)
                driver = get_object_or_404(Driver, id=driver_id)
            except Exception:
                messages.error(request, "فرستنده، گیرنده یا راننده معتبر نیستند.")
                return redirect('create_new')

            # تلاش برای یافتن خودروِ متعلق به راننده (اختیاری)
            # اگر ForeignKey از Vehicle به Driver دارید:
            vehicle = Vehicle.objects.filter(driver_id=driver.id).order_by('-id').first()
            # اگر related_name سفارشی دارید (مثلاً driver.vehicles)، خط بالا کافی است و نیازی به driver.vehicle نیست.

            # ذخیره‌سازی
            cargo = cargo_form.save()
            shipment = shipment_form.save(commit=False)
            shipment.sender = sender
            shipment.receiver = receiver
            shipment.cargo = cargo
            shipment.driver = driver
            if vehicle:  # فقط اگر ماشین یافت شد ست می‌کنیم
                shipment.vehicle = vehicle
            shipment.save()

            messages.success(request, "بیجک با موفقیت ثبت شد.")
            return redirect('success')
    else:
        cargo_form = CargoForm(prefix='cargo')
        shipment_form = ShipmentForm(prefix='shipment')

    return render(request, 'bijak/issuance_form.html', {
        'cargo_form': cargo_form,
        'shipment_form': shipment_form
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
            Q(cargo__name__icontains=query)
        )

    return render(request, 'bijak/bijak_search.html', {
        'shipments': shipments,
        'query': query
    })


# def search_sender(request):
#     query = request.GET.get('q', '')
#     results = Sender.objects.filter(name__icontains=query)[:10]
#     data = [{"id": r.id, "name": r.name, "phone": r.phone} for r in results]
#     return JsonResponse({"results": data})


def search_sender(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    # جستجو فقط بر اساس همون مقدار وارد شده (بدون حذف فاصله‌ها)
    senders = Sender.objects.filter(
        Q(name__icontains=query)
    )[:10]

    results = []
    for s in senders:
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
def save_sender(request):
    if request.method == "POST":
        sender_id = request.POST.get("id")
        name = request.POST.get("name")
        national_id = request.POST.get("national_id")
        postal = request.POST.get("postal")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if sender_id:  # اگر رکورد وجود داشت → ویرایش
            try:
                sender = Sender.objects.get(id=sender_id)
                sender.name = name
                sender.national_id = national_id
                sender.postal = postal
                sender.phone = phone
                sender.address = address
                sender.save()
            except Sender.DoesNotExist:
                return JsonResponse({"success": False, "error": "فرستنده یافت نشد"})
        else:  # ایجاد رکورد جدید
            sender = Sender.objects.create(
                name=name, national_id=national_id, postal=postal,
                phone=phone, address=address,
            )

        return JsonResponse({"success": True, "id": sender.id})

    return JsonResponse({"success": False, "error": "Invalid request"})


def search_receiver(request):
    query = request.GET.get('q', '').strip()
    if query:
        results = Receiver.objects.filter(name__icontains=query)[:10]
    else:
        results = []
    data = [{"id": r.id, "name": r.name, "phone": r.phone} for r in results]
    return JsonResponse({"results": data})


def search_driver(request):
    q = request.GET.get("q", "")
    drivers = Driver.objects.filter(name__icontains=q)[:10]

    results = []
    for d in drivers:
        try:
            vehicle = Vehicle.objects.get(driver=d)
            plate = vehicle.license_plate_three_digit
        except Vehicle.DoesNotExist:
            plate = ""

        results.append({
            "id": d.id,
            "name": d.name,
            "phone": d.phone,
            "plate_number": plate  # 👈 پلاک هم اضافه شد
        })
    return JsonResponse({"results": results})


def search_vehicle(request):
    q = request.GET.get("q", "")
    results = Vehicle.objects.filter(plate__icontains=q)[:10]
    return JsonResponse({"results": list(results.values("id", "plate"))})


# page render defs
def success_page(request):
    return render(request, 'secondary/success.html')


def search_page(request):
    return render(request, 'search.html')


# preview pages defs
def print_page(request, pk):
    shipment = Bijak.objects.select_related('sender', 'receiver', 'driver', 'vehicle', 'cargo').get(pk=pk)
    return render(request, 'secondary/print.html', {'shipment': shipment})


def preview_page(request, pk):
    bijak = Bijak.objects.select_related('sender', 'receiver', 'driver', 'vehicle', 'cargo').get(pk=pk)
    return render(request, 'secondary/preview.html', {'bijak': bijak})


# add date defs
def add_sender(request):
    if request.method == 'POST':
        form = SenderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_new')  # بازگشت به فرم بارنامه
    else:
        form = SenderForm()
    return render(request, 'add/add_sender.html', {"form": form})


def add_receiver(request):
    if request.method == 'POST':
        form = ReceiverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_new')  # بازگشت به فرم بارنامه
    else:
        form = ReceiverForm()
    return render(request, 'add/add_receiver.html', {"form": form})


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


def edit_sender(request):
    sender = None

    if request.method == 'POST':
        name = request.POST.get('name')  # نام وارد شده توسط کاربر
        sender = Sender.objects.filter(name__iexact=name).first()

        if sender:
            # اگر فرستنده پیدا شد → فرم پر بشه با اطلاعاتش
            form = SenderForm(request.POST, instance=sender)
        else:
            # اگر فرستنده جدید بود → فرم ایجاد رکورد جدید
            form = SenderForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('create_new')

    else:
        # GET request → نمایش فرم خالی
        form = SenderForm()

    return render(request, 'edit/edit_sender.html', {"form": form})


def edit_receiver(request):
    return render(request, 'edit/edit_receiver.html')


def edit_driver(request):
    return render(request, 'edit/edit_driver.html')


def edit_vehicle(request):
    return render(request, 'edit/edit_vehicle.html')


def edit_cargo(request):
    return render(request, 'edit/edit_cargo.html')


def edit_bijak(request):
    return render(request, 'secondary/print.html')
