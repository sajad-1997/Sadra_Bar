from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Receiver, Sender, Driver, Vehicle
from .forms import SenderForm, ReceiverForm, DriverForm, VehicleForm, CargoForm, ShipmentForm


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
    query = request.GET.get('q', '')
    results = Driver.objects.filter(name__icontains=query)[:10]
    data = [{"id": r.id, "name": r.name, "national_id": r.national_id} for r in results]
    return JsonResponse({"results": data})


def search_vehicle(request):
    query = request.GET.get('q', '')
    results = Vehicle.objects.filter(name__icontains=query)[:10]
    data = [{"id": r.id, "license_plate_three_digit": r.license_plate_three_digit,
             "license_plate_alphabet": r.license_plate_alphabet, "license_plate_two_digit": r.license_plate_two_digit}
            for r in results]
    return JsonResponse({"results": data})


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
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('form')  # بازگشت به فرم بارنامه
    else:
        form = VehicleForm()
    return render(request, 'add_vehicle.html', {'form': form})
