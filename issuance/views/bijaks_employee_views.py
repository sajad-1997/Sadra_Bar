# views_employee_bijaks.py

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from issuance.models import Bijak


@login_required
def pending_bijaks(request):
    """
    نمایش بارنامه‌های ایجاد شده توسط کارمند که در انتظار تأیید یا رد مدیریت هستند.
    """
    # فقط بارنامه‌های ایجاد شده توسط کاربر جاری و با وضعیت pending یا rejected
    search_query = request.GET.get('q', '').strip()

    # فیلتر بارنامه‌های کارمند جاری
    bijaks = Bijak.objects.filter(
        created_by=request.user,
        approval_status__in=['pending', 'rejected', 'approved']
    ).order_by('-id')

    # جستجو
    if search_query:
        bijaks = bijaks.filter(
            Q(id__icontains=search_query) |
            Q(sender__name__icontains=search_query) |
            Q(receiver__name__icontains=search_query) |
            Q(driver__name__icontains=search_query) |
            Q(vehicle__license_plate_series__icontains=search_query) |
            Q(vehicle__license_plate_two_digit__icontains=search_query) |
            Q(vehicle__license_plate_three_digit__icontains=search_query)
        )

    # صفحه‌بندی (10 بارنامه در هر صفحه)
    paginator = Paginator(bijaks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bijaks': page_obj,
        'search_query': search_query,
    }
    return render(request, 'issuance/bijak/bijak_list_waiting.html', context)
