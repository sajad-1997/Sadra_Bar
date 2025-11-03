from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse


def role_required(allowed_roles=None, redirect_url='forbidden'):
    """
    Decorator برای محدود کردن دسترسی کاربران بر اساس نقش (Role)

    استفاده:
    @role_required(['admin'])
    @role_required(['manager', 'admin'])
    """

    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # 🔹 اگر کاربر وارد نشده بود:
            if not user.is_authenticated:
                messages.warning(request, "برای مشاهده این صفحه ابتدا وارد شوید.")
                return redirect(reverse('login'))

            # 🔹 بررسی نقش کاربر
            user_role = getattr(user, 'role', None)
            if user_role not in allowed_roles:
                # اگر نقش مجاز نیست
                messages.error(request, "شما به این بخش دسترسی ندارید.")
                return redirect(reverse(redirect_url))  # صفحه 403 یا صفحه اصلی
                # یا می‌تونی بنویسی:
                # return HttpResponseForbidden("دسترسی غیرمجاز")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
