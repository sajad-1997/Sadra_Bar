from datetime import datetime
import pdfplumber
from django.db.models import Sum
from ..models.company import InsuranceCompany
from ..models.invoice import InsuranceInvoice
from ..models.policy import InsurancePolicy
from ..models.commission import InsuranceCommissionAllocation
from ..models.alert import InsuranceAlert
from issuance.models import Bijak


def parse_insurance_invoice(pdf_file, uploaded_by=None):
    """
    خواندن فایل PDF صورت‌حساب بیمه و ثبت رکورد در سیستم
    پارامتر uploaded_by: کاربر آپلود کننده PDF (برای تخصیص کمیسیون)
    """
    # باز کردن فایل PDF
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # -------------------------------
    # ۱. استخراج اطلاعات پایه صورت‌حساب
    # -------------------------------
    invoice_number = extract_between(text, "شماره صورت‌حساب:", "\n")
    invoice_date_str = extract_between(text, "تاریخ:", "\n")
    insurance_company_name = extract_between(text, "شرکت بیمه:", "\n")
    total_amount_str = extract_between(text, "مبلغ کل:", "\n")

    invoice_date = datetime.strptime(invoice_date_str.strip(), "%Y-%m-%d").date()
    total_amount = int(total_amount_str.replace(",", "").strip())

    # پیدا کردن شرکت بیمه
    company = InsuranceCompany.objects.filter(name=insurance_company_name).first()
    if not company:
        raise ValueError(f"شرکت بیمه {insurance_company_name} یافت نشد.")

    # -------------------------------
    # ۲. ایجاد رکورد Invoice
    # -------------------------------
    invoice = InsuranceInvoice.objects.create(
        invoice_number=invoice_number.strip(),
        insurance_company=company,
        issue_date=invoice_date,
        total_amount=total_amount,
        status='pending'
    )

    # -------------------------------
    # ۳. استخراج جزئیات هر بارنامه و ایجاد کمیسیون
    # -------------------------------
    extracted_rows_from_pdf = extract_bil_commission_rows(text)

    for row in extracted_rows_from_pdf:
        bil_number = row.get('bil_number')
        commission_amount = row.get('commission_amount', 0)

        try:
            bil = Bijak.objects.get(id=bil_number)
            InsuranceCommissionAllocation.objects.create(
                invoice=invoice,
                bil=bil,
                allocated_amount=commission_amount,
                allocated_by=uploaded_by,
                allocated_by_role=getattr(uploaded_by, 'role', None)
            )
        except Bijak.DoesNotExist:
            # لاگ کردن یا ادامه دادن
            continue

    # -------------------------------
    # ۴. ثبت هشدار بدهی
    # -------------------------------
    total_allocated = invoice.commissionallocation_set.aggregate(
        total_allocated=Sum('allocated_amount')
    )['total_allocated'] or 0

    remaining_amount = invoice.total_amount - total_allocated

    if remaining_amount > 0:
        InsuranceAlert.objects.create(
            invoice=invoice,
            alert_time=datetime.now(),
            status='pending'
        )

    return invoice


def extract_between(text, start_str, end_str):
    """
    استخراج متن بین دو رشته
    """
    try:
        start = text.index(start_str) + len(start_str)
        end = text.index(end_str, start)
        return text[start:end].strip()
    except ValueError:
        return ""


def extract_bil_commission_rows(text):
    """
    استخراج شماره بارنامه و مبلغ کمیسیون از متن PDF
    بازمی‌گرداند لیستی از دیکشنری:
    [{'bil_number': 123, 'commission_amount': 100000}, ...]
    توجه: باید بر اساس فرمت واقعی PDF تغییر کند
    """
    rows = []
    lines = text.split("\n")
    for line in lines:
        if "بارنامه:" in line:
            try:
                parts = line.split()
                bil_index = parts.index("بارنامه:") + 1
                amount_index = parts.index("کمیسیون:") + 1
                bil_number = int(parts[bil_index])
                commission_amount = int(parts[amount_index].replace(",", ""))
                rows.append({'bil_number': bil_number, 'commission_amount': commission_amount})
            except (ValueError, IndexError):
                continue
    return rows
