from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from issuance.models import Bijak


@login_required
def waiting_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("فقط مدیر اجازه دسترسی دارد")

    bijaks = Bijak.objects.filter(status="waiting_approval").order_by("-id")

    return render(request, "issuance/manager/waiting_list.html", {"bijaks": bijaks})
