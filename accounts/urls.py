from django.urls import path

from .views import CustomLoginView, CustomLogoutView, SuperAdminLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('super-admin-login/', SuperAdminLoginView.as_view(), name='super_admin_login'),
]
