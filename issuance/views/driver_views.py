# 2️⃣ driver_views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from ..forms import DriverForm
from ..models import Driver


@login_required
@never_cache
def add_driver(request):
    form = DriverForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('issuance:crud:create_new')
    return render(request, 'issuance/add/add_driver.html', {'form': form})


@login_required
@never_cache
def search_driver(request):
    q = request.GET.get('q', '')
    drivers = Driver.objects.filter(name__icontains=q)[:5]
    return JsonResponse({
        'results': list(drivers.values('id', 'name', 'national_id', 'phone'))
    })
