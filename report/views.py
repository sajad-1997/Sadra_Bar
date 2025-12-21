import jdatetime
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import render

from issuance.models import Bijak


def is_admin_or_manager(user):
    return user.is_superuser or user.groups.filter(name__in=['مدیر', 'مدیر کل سیستم']).exists()


@user_passes_test(is_admin_or_manager)
def report_dashboard(request):
    today = jdatetime.date.today()
    print("today", today)
    bijaks = Bijak.objects.all()

    # -----------------------
    # 🔹 خواندن مقادیر فیلتر از GET
    # -----------------------
    sender = request.GET.get('sender', '')
    receiver = request.GET.get('receiver', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # -----------------------
    # 🔹 اعمال فیلترها
    # -----------------------
    if sender:
        bijaks = bijaks.filter(sender__name__icontains=sender)

    if receiver:
        bijaks = bijaks.filter(receiver__name__icontains=receiver)

    # فیلتر بازه تاریخی با jdatetime
    if start_date_str:
        try:
            start_date = jdatetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            bijaks = bijaks.filter(issuance_datetime__gte=start_date)
        except Exception as e:
            print("⚠️ خطای تاریخ شروع:", e)

    if end_date_str:
        try:
            end_date = jdatetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            bijaks = bijaks.filter(issuance_datetime__lte=end_date)
        except Exception as e:
            print("⚠️ خطای تاریخ پایان:", e)

    # -----------------------
    # 🔹 آمارگیری
    # -----------------------
    daily_count = bijaks.filter(issuance_datetime=today).count()

    week_start = today - jdatetime.timedelta(days=today.weekday())
    week_end = week_start + jdatetime.timedelta(days=7)
    weekly_count = bijaks.filter(issuance_datetime__gte=week_start, issuance_datetime__lt=week_end).count()

    month_start = jdatetime.date(today.year, today.month, 1)
    month_end = (jdatetime.date(today.year + 1, 1, 1)
                 if today.month == 12
                 else jdatetime.date(today.year, today.month + 1, 1))
    monthly_count = bijaks.filter(issuance_datetime__gte=month_start, issuance_datetime__lt=month_end).count()

    year_start = jdatetime.date(today.year, 1, 1)
    year_end = jdatetime.date(today.year + 1, 1, 1)
    yearly_count = bijaks.filter(issuance_datetime__gte=year_start, issuance_datetime__lt=year_end).count()

    # -----------------------
    # 🔹 داده برای نمودار
    # -----------------------
    chart_data = (
        bijaks.values('issuance_datetime')
            .annotate(count=Count('issuance_datetime'))
            .order_by('issuance_datetime')
    )

    context = {
        'bijaks': bijaks,
        'daily_count': daily_count,
        'weekly_count': weekly_count,
        'monthly_count': monthly_count,
        'yearly_count': yearly_count,
        'chart_data': chart_data,
        'filters': {
            'sender': sender,
            'receiver': receiver,
            'start_date': start_date_str,
            'end_date': end_date_str,
        },
    }

    return render(request, 'report/report_dashboard.html', context)
