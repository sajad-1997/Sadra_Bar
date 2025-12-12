from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from issuance.models import Bijak, BijakApprovalLog


@login_required
def send_for_approval(request, bijak_id):
    bijak = get_object_or_404(Bijak, id=bijak_id)

    bijak.status = "waiting_approval"
    bijak.save()

    BijakApprovalLog.objects.create(
        bijak=bijak,
        user=request.user,
        action="sent_for_approval",
        description="ارسال جهت تایید مدیر"
    )

    messages.success(request, "بیجک با موفقیت برای تایید مدیر ارسال شد.")
    return redirect("bijak_detail", bijak_id=bijak.id)


@login_required
def approve_bijak(request, bijak_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("فقط مدیر اجازه تایید دارد")

    bijak = get_object_or_404(Bijak, id=bijak_id)

    bijak.status = "approved"
    bijak.save()

    BijakApprovalLog.objects.create(
        bijak=bijak,
        user=request.user,
        action="approved",
        description="تایید توسط مدیر"
    )

    messages.success(request, "بیجک تایید شد و مجوز چاپ گرفت.")
    return redirect("manager_waiting_list")


@login_required
def reject_bijak(request, bijak_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("فقط مدیر اجازه رد دارد")

    bijak = get_object_or_404(Bijak, id=bijak_id)

    reason = request.POST.get("reason")

    bijak.status = "rejected"
    bijak.save()

    BijakApprovalLog.objects.create(
        bijak=bijak,
        user=request.user,
        action="rejected",
        description=reason
    )

    messages.error(request, "بیجک رد شد.")
    return redirect("manager_waiting_list")
