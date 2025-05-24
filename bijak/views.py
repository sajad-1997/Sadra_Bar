from django.shortcuts import render, redirect
from .forms import SenderForm, ReceiverForm, DriverForm, VehicleForm, BijakForm


def create_all_forms(request):
    if request.method == 'POST':
        sender_form = SenderForm(request.POST, prefix='sender')
        receiver_form = ReceiverForm(request.POST, prefix='receiver')
        driver_form = DriverForm(request.POST, prefix='driver')
        vehicle_form = VehicleForm(request.POST, prefix='vehicle')
        shipment_form = BijakForm(request.POST, prefix='shipment')

        if all([sender_form.is_valid(), receiver_form.is_valid(), driver_form.is_valid(), vehicle_form.is_valid(),
                shipment_form.is_valid()]):
            sender = sender_form.save()
            receiver = receiver_form.save()
            driver = driver_form.save()
            vehicle = vehicle_form.save(commit=False)
            vehicle.driver = driver
            vehicle.save()

            shipment = shipment_form.save(commit=False)
            shipment.sender = sender
            shipment.receiver = receiver
            shipment.driver = driver
            shipment.vehicle = vehicle
            shipment.save()
            return redirect('success')
    else:
        sender_form = SenderForm(prefix='sender')
        receiver_form = ReceiverForm(prefix='receiver')
        driver_form = DriverForm(prefix='driver')
        vehicle_form = VehicleForm(prefix='vehicle')
        shipment_form = BijakForm(prefix='shipment')

    return render(request, 'full_form.html', {
        'sender_form': sender_form,
        'receiver_form': receiver_form,
        'driver_form': driver_form,
        'vehicle_form': vehicle_form,
        'shipment_form': shipment_form
    })


def success_page(request):
    return render(request, 'success.html')


def search_page(request):
    return render(request, 'search.html')
