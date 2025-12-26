# 4️⃣ customer_views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from issuance.models import Customer
from ..forms import CustomerForm


@login_required
@never_cache
def add_customer(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('issuance:crud:create_new')
    return render(request, 'issuance/add/add_customer.html', {"form": form})


@login_required
@never_cache
def search_customer(request):
    q = request.GET.get("q", "")
    customers = Customer.objects.filter(name__icontains=q)[:5]
    return JsonResponse({"results": list(customers.values())})


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
def edit_customer(request):
    return render(request, 'issuance/edit/edit_customer.html')
