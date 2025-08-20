from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Receiver, Sender, Driver, Vehicle
from .forms import SenderForm, ReceiverForm, DriverForm, VehicleForm, CargoForm, ShipmentForm, CarPlateForm


def create_all_forms(request):
    receivers = Receiver.objects.all()

    if request.method == 'POST':
        sender_form = SenderForm(request.POST, prefix='sender')
        receiver_form = ReceiverForm(request.POST, prefix='receiver')
        cargo_form = CargoForm(request.POST, prefix='cargo')
        driver_form = DriverForm(request.POST, prefix='driver')
        vehicle_form = VehicleForm(request.POST, prefix='vehicle')
        shipment_form = ShipmentForm(request.POST, prefix='shipment')

        if all([sender_form.is_valid(), receiver_form.is_valid(), cargo_form.is_valid(), driver_form.is_valid(),
                vehicle_form.is_valid(), shipment_form.is_valid()]):
            sender = sender_form.save()
            receiver = receiver_form.save()
            cargo = cargo_form.save()
            driver = driver_form.save()
            vehicle = vehicle_form.save(commit=False)
            vehicle.driver = driver
            vehicle.save()

            shipment = shipment_form.save(commit=False)
            shipment.sender = sender
            shipment.receiver = receiver
            shipment.cargo = cargo
            shipment.driver = driver
            shipment.vehicle = vehicle
            shipment.save()
            return redirect('success')
    else:
        sender_form = SenderForm(prefix='sender')
        receiver_form = ReceiverForm(prefix='receiver')
        cargo_form = CargoForm(prefix='cargo')
        driver_form = DriverForm(prefix='driver')
        vehicle_form = VehicleForm(prefix='vehicle')
        shipment_form = ShipmentForm(prefix='shipment')

    return render(request, 'issuance_form.html', {
        'sender_form': sender_form,
        'receiver_form': receiver_form,
        'receivers': receivers,
        'cargo_form': cargo_form,
        'driver_form': driver_form,
        'vehicle_form': vehicle_form,
        'shipment_form': shipment_form
    })


def search_sender(request):
    query = request.GET.get('q', '')
    results = Sender.objects.filter(name__icontains=query)[:10]
    data = [{"id": r.id, "name": r.name, "phone": r.phone} for r in results]
    return JsonResponse({"results": data})


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
    return render(request, 'success.html')


def search_page(request):
    return render(request, 'search.html')


def print_page(request):
    return render(request, 'print.html')


# add date defs

def add_sender(request):
    if request.method == 'POST':
        form = SenderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('form')  # بازگشت به فرم بارنامه
    else:
        form = SenderForm()
    return render(request, 'add_sender.html', {'form': form})


def add_receiver(request):
    if request.method == 'POST':
        form = ReceiverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('form')  # بازگشت به فرم بارنامه
    else:
        form = ReceiverForm()
    return render(request, 'add_receiver.html', {'form': form})


def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('form')  # بازگشت به فرم بارنامه
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})


def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            # vehicle = form.save()
            # return redirect("show_plate", vehicle_id=vehicle.id)
            return redirect('form')  # بازگشت به فرم بارنامه
    else:
        form = VehicleForm()
    return render(request, "add_vehicle.html", {"form": form})


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
