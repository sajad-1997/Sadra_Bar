import re
from datetime import datetime
from datetime import time
from io import BytesIO

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
# from .utils import num_to_word_rial
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from khayyam import JalaliDatetime

from .forms import *
# from .models import Customer, Driver, Vehicle, Caption, Bijak, BijakApprovalLog
from .models import Customer, Driver, Vehicle, Caption, Bijak

FIELD_LABELS = {
    # Shipment
    "issuance_date": "تاریخ صدور بارنامه",
    "issuance_time": "ساعت صدور بارنامه",
    "sender": "فرستنده",
    "receiver": "گیرنده",
    "driver": "راننده",
    "vehicle": "وسیله نقلیه",

    # Cargo
    "weight": "وزن محموله",
    "cargo_type": "نوع محموله",
    "origin": "مبدأ",
    "destination": "مقصد",
}

ERROR_TRANSLATIONS = {
    "This field is required.": "تکمیل این فیلد الزامی است.",
    "Enter a valid date.": "تاریخ وارد شده معتبر نیست.",
    "Enter a valid time.": "ساعت وارد شده معتبر نیست.",
    "Enter a valid value.": "مقدار وارد شده معتبر نیست.",
    "Ensure this value is greater than or equal to 0.": "مقدار وارد شده نمی‌تواند منفی باشد.",

    # 🔴 خطای datetime
    "Enter a valid date/time in YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.":
        "تاریخ یا ساعت صدور بارنامه به‌درستی وارد نشده است.",
}

ERROR_PRIORITY = [
    "sender",
    "receiver",
    "driver",
    "issuance_date",
    "issuance_time",
]


def show_form_errors(request, form, section_title=None):
    """
    Helper نهایی:
    - پشتیبانی از non-field errors (__all__)
    - ترجمه خطاهای datetime
    - خروجی کاملاً قابل فهم برای کاربر
    """

    for field, errors in form.errors.items():

        # 🟡 خطاهای کلی فرم
        if field == "__all__":
            for error in errors:
                readable_error = ERROR_TRANSLATIONS.get(error, error)

                if section_title:
                    messages.error(
                        request,
                        f"{section_title}: {readable_error}"
                    )
                else:
                    messages.error(request, readable_error)
            continue

        # 🟢 خطاهای مربوط به فیلد
        if field in form.fields:
            field_label = form.fields[field].label
        else:
            field_label = FIELD_LABELS.get(field, field)

        for error in errors:
            readable_error = ERROR_TRANSLATIONS.get(error, error)

            if section_title:
                message = f"{section_title} - {field_label}: {readable_error}"
            else:
                message = f"{field_label}: {readable_error}"

            messages.error(request, message)


def persian_to_english_numbers(value):
    """تبدیل اعداد فارسی به انگلیسی برای ذخیره‌سازی"""
    persian = '۰۱۲۳۴۵۶۷۸۹'
    english = '0123456789'
    table = str.maketrans(persian, english)
    return value.translate(table)


def convert_jalali_to_gregorian(date_str):
    """
    تبدیل تاریخ شمسی (۱۴۰۳/۱۰/۱۵) به میلادی
    """
    date_str = persian_to_english_numbers(date_str)
    y, m, d = map(int, date_str.split('/'))
    g = JalaliDate(y, m, d).todate()
    return g  # returns Python date()


def convert_time_farsi_to_time(time_str):
    """
    تبدیل ساعت فارسی به python.time()
    """
    time_str = persian_to_english_numbers(time_str)
    match = re.match(r'^(\d{1,2}):(\d{1,2})$', time_str)
    if not match:
        return time(0, 0)

    hour = int(match.group(1))
    minute = int(match.group(2))
    return time(hour, minute)


def to_jalali(date_obj):
    if not date_obj:
        return "—"
    try:
        return jdatetime.date.fromgregorian(date=date_obj).strftime("%Y/%m/%d")
    except:
        return "—"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'issuance/base.html'


class StaffOnlyView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'issuance/bijak/issuance_form.html'

    def test_func(self):
        return self.request.user.role in ['admin', 'manager', 'staff']


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# بیجک جدید (ثبت)
# -----------------------
# def create_new(request):
#     """ایجاد بیجک جدید"""
#
#     if request.method == 'POST':
#         action = request.POST.get('action')
#
#         sender_id = request.POST.get("sender")
#         receiver_id = request.POST.get("receiver")
#         driver_id = request.POST.get("driver")
#         selected_caption_id = request.POST.get("selected_caption")
#         manual_text = request.POST.get("manual_description", "").strip()
#
#         # تبدیل تاریخ و زمان
#         jalali_date = request.POST.get("shipment-issuance_date")
#         jalali_time = request.POST.get("shipment-issuance_time")
#         try:
#             greg_date = convert_jalali_to_gregorian(jalali_date)
#             time_obj = convert_time_farsi_to_time(jalali_time)
#         except Exception as e:
#             messages.error(request, "خطا در تبدیل تاریخ یا ساعت.")
#             print(f"Date/Time conversion error: {e}")
#             # بازگرداندن فرم با مقادیر وارد شده
#             shipment_form = ShipmentForm(request.POST, prefix='shipment')
#             cargo_form = CargoForm(request.POST, prefix='cargo')
#             captions = Caption.objects.all().order_by('-id')
#             return render(request, 'issuance/bijak/issuance_form.html', {
#                 'shipment_form': shipment_form,
#                 'cargo_form': cargo_form,
#                 'captions': captions,
#             })
#
#         shipment_form = ShipmentForm(request.POST, prefix='shipment')
#         cargo_form = CargoForm(request.POST, prefix='cargo')
#
#         if shipment_form.is_valid() and cargo_form.is_valid():
#             try:
#                 sender = get_object_or_404(Customer, id=sender_id)
#                 receiver = get_object_or_404(Customer, id=receiver_id)
#                 driver = get_object_or_404(Driver, id=driver_id)
#             except Exception as e:
#                 messages.error(request, "فرستنده، گیرنده یا راننده معتبر نیستند.")
#                 print(f"Customer/Driver fetch error: {e}")
#                 captions = Caption.objects.all().order_by('-id')
#                 return render(request, 'issuance/bijak/issuance_form.html', {
#                     'shipment_form': shipment_form,
#                     'cargo_form': cargo_form,
#                     'captions': captions,
#                 })
#
#             vehicle = Vehicle.objects.filter(driver_id=driver.id).order_by('-id').first()
#
#             with transaction.atomic():
#                 cargo = cargo_form.save()
#
#                 bijak = shipment_form.save(commit=False)
#                 bijak.sender = sender
#                 bijak.receiver = receiver
#                 bijak.driver = driver
#                 bijak.vehicle = vehicle
#                 bijak.cargo = cargo
#
#                 bijak.issuance_date = greg_date
#                 bijak.issuance_time = time_obj
#                 bijak.status = "draft"
#                 bijak.approval_status = "pending"
#
#                 if selected_caption_id:
#                     try:
#                         bijak.selected_caption = Caption.objects.get(id=selected_caption_id)
#                     except Caption.DoesNotExist:
#                         pass
#
#                 if manual_text:
#                     Caption.objects.create(content=manual_text)
#                     bijak.custom_caption = manual_text
#
#                 bijak.save()
#
#             if action == 'print':
#                 return redirect('bijak_print', bijak_id=bijak.id)
#             elif action == 'send_for_approval':
#                 return redirect('send_for_approval', bijak_id=bijak.id)
#
#             messages.success(request, "بیجک با موفقیت ثبت شد.")
#             return redirect('preview', pk=bijak.id)
#
#         else:
#             # نمایش دقیق خطاهای هر فرم بدون از دست رفتن مقادیر وارد شده
#             for form_name, form_instance in [('Shipment Form', shipment_form), ('Cargo Form', cargo_form)]:
#                 if not form_instance.is_valid():
#                     for field, errors in form_instance.errors.items():
#                         for error in errors:
#                             messages.error(request, f"{form_name} - {field}: {error}")
#                             print("issuance_time:", request.POST.get("shipment-issuance_time"))
#                             print(f"{form_name} - {field}: {error}")
#
#             captions = Caption.objects.all().order_by('-id')
#             return render(request, 'issuance/bijak/issuance_form.html', {
#                 'shipment_form': shipment_form,
#                 'cargo_form': cargo_form,
#                 'captions': captions,
#             })
#
#     else:
#         shipment_form = ShipmentForm(prefix='shipment')
#         cargo_form = CargoForm(prefix='cargo')
#
#     captions = Caption.objects.all().order_by('-id')
#
#     return render(request, 'issuance/bijak/issuance_form.html', {
#         'shipment_form': shipment_form,
#         'cargo_form': cargo_form,
#         'captions': captions,
#     })
def create_new(request):
    """
    ایجاد بارنامه:
    - ثبت اولیه
    - ارسال برای تأیید مدیر
    - مدیریت پیام و ریدایرکت
    """

    captions = Caption.objects.all().order_by('-id')
    if request.method != 'POST':
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': ShipmentForm(prefix='shipment'),
            'cargo_form': CargoForm(prefix='cargo'),
            'captions': captions,
        })

    shipment_form = ShipmentForm(request.POST, prefix='shipment')
    cargo_form = CargoForm(request.POST, prefix='cargo')

    if not (shipment_form.is_valid() and cargo_form.is_valid()):
        show_form_errors(request, shipment_form, "اطلاعات بارنامه")
        show_form_errors(request, cargo_form, "اطلاعات محموله")
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': shipment_form,
            'cargo_form': cargo_form,
            'captions': captions,
        })

    # ---------- تاریخ و ساعت ----------
    try:
        date_str = persian_to_english_numbers(
            shipment_form.cleaned_data['issuance_date']
        )
        time_str = persian_to_english_numbers(
            shipment_form.cleaned_data['issuance_time']
        )

        j_date = JalaliDatetime.strptime(date_str, "%Y/%m/%d")
        hour, minute = map(int, time_str.split(':'))

        issuance_datetime = datetime(
            j_date.year, j_date.month, j_date.day,
            hour, minute
        )
    except Exception:
        messages.error(request, "تاریخ یا ساعت وارد شده معتبر نیست.")
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': shipment_form,
            'cargo_form': cargo_form,
            'captions': captions,
        })

    # ---------- دریافت اشخاص ----------
    try:
        sender = Customer.objects.get(id=request.POST.get("sender"))
        receiver = Customer.objects.get(id=request.POST.get("receiver"))
        driver = Driver.objects.get(id=request.POST.get("driver"))
        vehicle = Vehicle.objects.filter(driver=driver).last()
    except Exception:
        messages.error(request, "فرستنده، گیرنده یا راننده معتبر نیست.")
        return render(request, 'issuance/bijak/issuance_form.html', {
            'shipment_form': shipment_form,
            'cargo_form': cargo_form,
            'captions': captions,
        })

    action = request.POST.get("action")

    # ---------- ذخیره ----------
    with transaction.atomic():
        cargo = cargo_form.save()

        bijak = shipment_form.save(commit=False)
        bijak.sender = sender
        bijak.receiver = receiver
        bijak.driver = driver
        bijak.vehicle = vehicle
        bijak.cargo = cargo
        bijak.issuance_datetime = issuance_datetime

        # وضعیت بر اساس اکشن
        if action == "send_for_approval":
            bijak.status = "waiting_approval"
        else:
            bijak.status = "draft"

        bijak.save()

    # ---------- پیام و ریدایرکت ----------
    if action == "send_for_approval":
        messages.success(
            request,
            "بارنامه با موفقیت ثبت و برای تأیید مدیریت ارسال شد."
        )
        return redirect("issuance:manager:waiting_list")

    messages.success(request, "بارنامه ذخیره شد.")
    return redirect("issuance:preview", pk=bijak.pk)


def _show_form_errors(form, form_name):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(
                form.request if hasattr(form, 'request') else None,
                f"{form_name} - {field}: {error}"
            )


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# تاییده بیجک ها
# -----------------------

@login_required
# def approve_bijak(request, bijak_id):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("فقط مدیر اجازه تایید دارد")
#
#     bijak = get_object_or_404(Bijak, id=bijak_id)
#
#     bijak.status = "approved"
#     bijak.save()
#
#     BijakApprovalLog.objects.create(
#         bijak=bijak,
#         user=request.user,
#         action="approved",
#         description="تایید توسط مدیر"
#     )
#
#     messages.success(request, "بیجک تایید شد و مجوز چاپ گرفت.")
#     return redirect("manager_waiting_list")

@login_required
# def reject_bijak(request, bijak_id):
#     if not request.user.is_staff:
#         return HttpResponseForbidden("فقط مدیر اجازه رد دارد")
#
#     bijak = get_object_or_404(Bijak, id=bijak_id)
#
#     reason = request.POST.get("reason")
#
#     bijak.status = "rejected"
#     bijak.save()
#
#     BijakApprovalLog.objects.create(
#         bijak=bijak,
#         user=request.user,
#         action="rejected",
#         description=reason
#     )
#
#     messages.error(request, "بیجک رد شد.")
#     return redirect("manager_waiting_list")

@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# افزودن مشتری، راننده، وسیله و توضیح
# -----------------------
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)  # رکورد هنوز ذخیره نشده
            customer.save()
            return redirect('issuance:crud:create_new')  # بازگشت به فرم بارنامه
    else:
        form = CustomerForm()
    return render(request, 'issuance/add/add_customer.html', {"form": form})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save()
            messages.success(request, "راننده با موفقیت ذخیره شد.")
            return redirect('issuance:crud:create_new')  # بازگشت به فرم بارنامه
        else:
            messages.error(request, "خطا در ثبت فرم. لطفاً دوباره بررسی کنید.")
    else:
        form = DriverForm()

    return render(request, 'issuance/add/add_driver.html', {"form": form})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)  # رکورد هنوز ذخیره نشده
            vehicle.save()
            return redirect('issuance:crud:create_new')  # بازگشت به فرم بارنامه
    else:
        form = VehicleForm()
    return render(request, "issuance/add/add_vehicle.html", {"form": form})


# def get_vehicle_by_driver(request):
#     driver_id = request.GET.get("driver_id")
#     try:
#         vehicle = Vehicle.objects.get(driver_id=driver_id)
#         data = {
#             "two_digit": vehicle.license_plate_two_digit,
#             "alphabet": vehicle.license_plate_alphabet,
#             "three_digit": vehicle.license_plate_three_digit,
#             "series": vehicle.license_plate_series,
#         }
#         return JsonResponse({"success": True, "vehicle": data})
#     except Vehicle.DoesNotExist:
#         return JsonResponse({"success": False, "error": "وسیله‌ای برای این راننده پیدا نشد"})
def get_vehicle_by_driver(request):
    driver_id = request.GET.get("driver_id")

    vehicle = (
        Vehicle.objects
            .filter(driver_id=driver_id)
            .order_by('-id')
            .first()
    )

    if not vehicle:
        return JsonResponse({
            "success": False,
            "error": "برای این راننده خودروی فعالی ثبت نشده است"
        })

    data = {
        "two_digit": vehicle.license_plate_two_digit,
        "alphabet": vehicle.license_plate_alphabet,
        "three_digit": vehicle.license_plate_three_digit,
        "series": vehicle.license_plate_series,
    }

    return JsonResponse({"success": True, "vehicle": data})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def add_caption(request):
    if request.method == "POST":
        form = CaptionForm(request.POST)
        if form.is_valid():
            caption = form.save(commit=False)  # رکورد هنوز ذخیره نشده
            caption.save()
            messages.success(request, "✅ توضیحات با موفقیت ذخیره شد.")
            return redirect("create_new")
    else:
        form = CaptionForm()

    return render(request, 'issuance/add/add_caption.html', {"form": form})


def to_words_view(request):
    num = request.GET.get("num", "0")
    words = num_to_word_rial(num)
    return JsonResponse({"words": words})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# جستجوی بیجک
# -----------------------
# def search_shipment(request):
#     query = request.GET.get('q', '').strip()
#     shipments = Bijak.objects.all()
#
#     if query:
#         shipments = shipments.filter(
#             Q(sender__name__icontains=query) |
#             Q(receiver__name__icontains=query) |
#             Q(driver__name__icontains=query) |
#             Q(vehicle__license_plate_two_digit__icontains=query) |
#             Q(vehicle__license_plate_three_digit__icontains=query) |
#             Q(vehicle__license_plate_alphabet__icontains=query) |
#             Q(vehicle__license_plate_series__icontains=query) |
#             Q(cargo__name__icontains=query) |
#             Q(cargo__origin__icontains=query) |
#             Q(cargo__destination__icontains=query) |
#             Q(selected_caption__content__icontains=query)  # تغییر به selected_caption
#         )
#
#     return render(request, 'issuance/secondary/search.html', {
#         'shipments': shipments,
#         'query': query
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


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# جستجوها مشتری ها
# -----------------------
def search_customer(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    # جستجو فقط بر اساس همون مقدار وارد شده (بدون حذف فاصله‌ها)
    customers = Customer.objects.filter(
        Q(name__icontains=query)
    )[:5]

    results = []
    for c in customers:
        results.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "address": c.address,
            "national_id": c.national_id,
            "postal": c.postal,
        })

    return JsonResponse({"results": results})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# جستجوها راننده ها
# -----------------------
def search_driver(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    drivers = Driver.objects.filter(
        Q(name__icontains=query)
    )[:5]

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
            "driver_smart_card": d.driver_smart_card,
            "insurance_policy_number": d.insurance_policy_number,
            "insurance_policy_expiry": d.insurance_policy_expiry,

        })
    return JsonResponse({"results": results})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
@csrf_exempt
def save_customer(request):
    if request.method == "POST":
        customer_id = request.POST.get("id")

        if customer_id:  # ویرایش
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({"success": False, "error": "مشتری یافت نشد"})

            # فرم با instance و داده‌های POST
            form = CustomerForm(request.POST, instance=customer)
        else:  # ایجاد
            form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()
            return JsonResponse({"success": True, "id": customer.id})
        else:
            # ارورها را برای نمایش در کلاینت برگردان
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def duplicate_customer(request):
    if request.method == "POST":
        try:
            # رکورد جدید بساز
            new_customer = Customer.objects.create(
                name=request.POST.get("name"),
                national_id=request.POST.get("national_id"),
                postal=request.POST.get("postal"),
                phone=request.POST.get("phone"),
                address=request.POST.get("address"),
            )

            return JsonResponse({"success": True, "new_id": new_customer.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "درخواست نامعتبر"})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
@csrf_exempt
def save_driver(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})

    driver_id = request.POST.get("id")

    # دریافت فیلدها
    name = request.POST.get("name", "").strip()
    national_id = request.POST.get("national_id", "").strip()
    residence = request.POST.get("residence", "").strip()
    father_name = request.POST.get("father_name", "").strip()
    birth_date = request.POST.get("birth_date", "").strip() or None
    certificate_date = request.POST.get("certificate_date", "").strip() or None
    certificate = request.POST.get("certificate", "").strip()
    phone = request.POST.get("phone", "").strip()
    phone2 = request.POST.get("phone2", "").strip()
    address = request.POST.get("address", "").strip()
    driver_smart_card = request.POST.get("driver_smart_card", "").strip() or None
    insurance_policy_number = request.POST.get("insurance_policy_number", "").strip() or None
    insurance_policy_expiry = request.POST.get("insurance_policy_expiry", "").strip() or None

    # ---------------------------------------
    # 1) اعتبارسنجی فیلدهای اجباری
    # ---------------------------------------
    required_fields = {
        "name": "نام و نام خانوادگی الزامی است",
        "national_id": "کد ملی الزامی است",
        "certificate": "شماره گواهینامه الزامی است",
        "phone": "شماره تلفن راننده الزامی است",
    }

    for field_key, error_msg in required_fields.items():
        if not locals()[field_key]:
            return JsonResponse({
                "success": False,
                "error": error_msg,
                "field": field_key
            })

    # ---------------------------------------
    # 2) تبدیل جلالی → میلادی
    # ---------------------------------------
    if birth_date:
        birth_date = persian_to_gregorian(birth_date)

    if certificate_date:
        certificate_date = persian_to_gregorian(certificate_date)

    # ---------------------------------------
    # 3) بررسی عدم تکرار (کد ملی – گواهینامه)
    # ---------------------------------------
    if driver_id:
        # حالت ویرایش
        if Driver.objects.filter(national_id=national_id).exclude(id=driver_id).exists():
            return JsonResponse({"success": False, "error": "این کد ملی برای راننده دیگری ثبت شده است"})
        if Driver.objects.filter(certificate=certificate).exclude(id=driver_id).exists():
            return JsonResponse({"success": False, "error": "این شماره گواهینامه برای راننده دیگری ثبت شده است"})
    else:
        # ایجاد جدید
        if Driver.objects.filter(national_id=national_id).exists():
            return JsonResponse({"success": False, "error": "این کد ملی قبلاً ثبت شده است"})
        if Driver.objects.filter(certificate=certificate).exists():
            return JsonResponse({"success": False, "error": "این شماره گواهینامه قبلاً ثبت شده است"})

    # ---------------------------------------
    # 4) ذخیره‌سازی (ویرایش یا ایجاد)
    # ---------------------------------------
    if driver_id:
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({"success": False, "error": "راننده یافت نشد"})
    else:
        driver = Driver()

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
    driver.driver_smart_card = driver_smart_card
    driver.insurance_policy_number = insurance_policy_number
    driver.insurance_policy_expiry = insurance_policy_expiry
    driver.save()

    # ---------------------------------------
    # 5) بازگشت به صفحه قبل
    # ---------------------------------------
    previous_url = request.META.get("HTTP_REFERER", "/")

    return JsonResponse({
        "success": True,
        "message": "اطلاعات راننده با موفقیت ذخیره شد",
        "id": driver.id,
        "redirect": previous_url
    })


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
@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# جستجوها خودرو ها
# -----------------------
def search_vehicle(request):
    q = request.GET.get("q", "")
    results = Vehicle.objects.filter(plate__icontains=q)[:10]
    return JsonResponse({"results": list(results.values("id", "plate"))})


# page render defs
def success_page(request):
    return render(request, 'issuance/secondary/success.html')


# -----------------------
# پیش‌نمایش و چاپ
# -----------------------
def print_page(request, pk):
    shipment = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo', 'selected_caption'
    ).get(pk=pk)

    # چون issuance_date از نوع jDateField هست، مستقیم قابل فرمت‌دهی به شکل شمسی است
    jalali_date = jdatetime.date.fromgregorian(date=shipment.issuance_date).strftime("%Y/%m/%d")

    context = {
        'shipment': shipment,
        'jalali_date': jalali_date,
    }
    print("issuance_date:", shipment.issuance_date, type(shipment.issuance_date))
    return render(request, 'issuance/secondary/print.html', context)


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def preview_page(request, pk):
    bijak = Bijak.objects.select_related(
        'sender', 'receiver', 'driver', 'vehicle', 'cargo', 'selected_caption'
    ).get(pk=pk)
    return render(request, 'issuance/secondary/preview.html', {'bijak': bijak})


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def bijak_last_view(request, pk):
    # bijak = Bijak.objects.last()  # آخرین رکورد جدول
    if pk:
        bijak = get_object_or_404(Bijak, pk=pk)
    else:
        bijak = Bijak.objects.last()

    # دسترسی به راننده
    driver = bijak.driver

    # تبدیل تمام تاریخ‌ها به رشته شمسی
    issuance_date = bijak.issuance_datetime.strftime("%Y/%m/%d")
    issuance_time = bijak.issuance_datetime.strftime("%Y/%m/%d")
    birth_date = to_jalali(driver.birth_date)
    license_issue_date = to_jalali(driver.certificate_date)

    context = {
        'bijak': bijak,
        'jalali_issuance_date': issuance_date,
        'jalali_birth_date': birth_date,
        'jalali_license_issue_date': license_issue_date,
    }

    return render(request, "issuance/bijak/final_bijak.html", context)


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def edit_customer(request):
    return render(request, 'issuance/edit/edit_customer.html')


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def edit_driver(request):
    return render(request, 'issuance/edit/edit_driver.html')


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def edit_vehicle(request):
    return render(request, 'issuance/edit/edit_vehicle.html')


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
def edit_cargo(request):
    return render(request, 'issuance/edit/edit_cargo.html')


@login_required(login_url='/accounts/login/')
@never_cache  # جلوگیری از نمایش از کش
# -----------------------
# ویرایش بارنامه صادر شده
# -----------------------
def edit_bijak(request):
    bijak = get_object_or_404(Bijak)

    if request.method == 'POST':
        bijak_form = ShipmentForm(request.POST, instance=bijak)
        sender_form = CustomerForm(request.POST, prefix='sender', instance=bijak.sender)
        receiver_form = CustomerForm(request.POST, prefix='receiver', instance=bijak.receiver)
        driver_form = DriverForm(request.POST, prefix='driver', instance=bijak.driver)
        vehicle_form = VehicleForm(request.POST, instance=bijak.vehicle)
        cargo_form = CargoForm(request.POST, instance=bijak.cargo)

        if all([
            bijak_form.is_valid(),
            sender_form.is_valid(),
            receiver_form.is_valid(),
            driver_form.is_valid(),
            vehicle_form.is_valid(),
            cargo_form.is_valid()
        ]):
            bijak_form.save()
            sender_form.save()
            receiver_form.save()
            driver_form.save()
            vehicle_form.save()
            cargo_form.save()

            messages.success(request, "بیجک با موفقیت ویرایش شد ✅")
            return redirect('preview', pk=bijak.pk)  # صفحه نمایش نهایی
    else:
        bijak_form = ShipmentForm(instance=bijak)
        sender_form = CustomerForm(prefix='sender', instance=bijak.sender)
        receiver_form = CustomerForm(prefix='receiver', instance=bijak.receiver)
        driver_form = DriverForm(prefix='driver', instance=bijak.driver)
        vehicle_form = VehicleForm(instance=bijak.vehicle)
        cargo_form = CargoForm(instance=bijak.cargo)

    return render(request, 'issuance/edit/edit_bijak.html', {
        'bijak_form': bijak_form,
        'sender_form': sender_form,
        'receiver_form': receiver_form,
        'driver_form': driver_form,
        'vehicle_form': vehicle_form,
        'cargo_form': cargo_form,
        'bijak': bijak,
    })


# -----------------------
# بارکد بارنامه صادر شده
# -----------------------
def bijak_qr(request, pk):
    bijak = get_object_or_404(Bijak, pk=pk)

    # لینک مقصد: صفحه چاپ بارنامه
    url = request.build_absolute_uri(f"/Barnameh/{pk}/print/")

    # تولید QR
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")
