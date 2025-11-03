from django.urls import path

from .views import admin_dashboard, manager_dashboard, staff_dashboard

urlpatterns = [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('staff/', staff_dashboard, name='staff_dashboard'),
]
