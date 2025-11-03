# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('admin_dashboard')
        elif user.role == 'manager':
            return reverse_lazy('manager_dashboard')
        elif user.role == 'staff':
            return reverse_lazy('staff_dashboard')
        else:
            return reverse_lazy('home')


class SuperAdminLoginView(LoginView):
    template_name = 'accounts/super_admin_login.html'

    def get_success_url(self):
        user = self.request.user
        # فقط کاربری با نقش admin اجازه ورود داره
        if user.role == 'admin':
            return reverse_lazy('admin_dashboard')
        else:
            return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    """
       خروج امن از سیستم و ری‌دایرکت کاربر به صفحه اصلی با پیام
       """
    next_page = ''  # صفحه‌ای که بعد از خروج به آن منتقل شود (مثلاً صفحه اصلی)

    def dispatch(self, request, *args, **kwargs):
        # اضافه کردن پیام خروج
        if request.user.is_authenticated:
            # messages.success(request, f"کاربر {request.user.username} با موفقیت خارج شد.")
            pass
        return super().dispatch(request, *args, **kwargs)
