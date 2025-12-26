# 2️⃣ driver_views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
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


@login_required
@never_cache
def edit_driver(request, driver_id):
    driver = get_object_or_404(Driver, pk=driver_id)
    form = DriverForm(request.POST or None, instance=driver)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            now = timezone.now()

            # مدیریت تاریخ ایجاد و بروزرسانی
            if not getattr(instance, 'created_at', None):
                instance.created_at = now
            instance.updated_at = now

            if not getattr(instance, 'created_by', None):
                instance.created_by = request.user
            instance.updated_by = request.user

            instance.save()
            messages.success(request, "اطلاعات راننده با موفقیت ذخیره شد.")
            return redirect('issuance:crud:create_new')
        else:
            # نمایش پیام خطا برای هر فیلد
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

    return render(request, 'issuance/edit/edit_driver.html', {'form': form, 'driver': driver})
