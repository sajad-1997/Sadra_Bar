# 5️⃣ search_views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

from ..models import Bijak


@login_required
# def search_shipment(request):
#     q = request.GET.get('q', '')
#     bijaks = Bijak.objects.filter(tracking_code__icontains=q)[:5]
#
#     return JsonResponse({
#         'results': list(
#             bijaks.values(
#                 'id',
#                 'tracking_code',
#                 'sender',
#                 'receiver'
#             )
#         )
#     })
def search_shipment(request):
    template_name = "issuance/search/search.html"

    query = Bijak.objects.all().order_by('-created_at')

    # فیلدهای جستجو
    tracking = request.GET.get('tracking')
    sender = request.GET.get('sender')
    receiver = request.GET.get('receiver')
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    driver = request.GET.get('driver')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # بخش‌های پلاک جداگانه
    plate_two_digit = request.GET.get('plate_two_digit')
    plate_alphabet = request.GET.get('plate_alphabet')
    plate_three_digit = request.GET.get('plate_three_digit')
    plate_series = request.GET.get('plate_series')

    # فیلترهای ساده
    if tracking:
        query = query.filter(tracking_code__icontains=tracking)

    if sender:
        query = query.filter(sender__name__icontains=sender)

    if receiver:
        query = query.filter(receiver__name__icontains=receiver)

    if origin:
        query = query.filter(origin__icontains=origin)

    if destination:
        query = query.filter(destination__icontains=destination)

    if driver:
        query = query.filter(driver__name__icontains=driver)

    if start_date:
        query = query.filter(created_at__date__gte=start_date)

    if end_date:
        query = query.filter(created_at__date__lte=end_date)

    # فیلتر بر اساس پلاک بخش‌بخش
    if plate_two_digit:
        query = query.filter(vehicle__license_plate_two_digit__icontains=plate_two_digit)
    if plate_alphabet:
        query = query.filter(vehicle__license_plate_alphabet__icontains=plate_alphabet)
    if plate_three_digit:
        query = query.filter(vehicle__license_plate_three_digit__icontains=plate_three_digit)
    if plate_series:
        query = query.filter(vehicle__license_plate_series__icontains=plate_series)

    context = {
        "bijaks": query,
        # نگهداری مقادیر فیلترها برای نمایش در فرم
        "filters": {
            "tracking": tracking or "",
            "sender": sender or "",
            "receiver": receiver or "",
            "origin": origin or "",
            "destination": destination or "",
            "driver": driver or "",
            "start_date": start_date or "",
            "end_date": end_date or "",
            "plate_two_digit": plate_two_digit or "",
            "plate_alphabet": plate_alphabet or "",
            "plate_three_digit": plate_three_digit or "",
            "plate_series": plate_series or "",
        }
    }

    return render(request, template_name, context)
