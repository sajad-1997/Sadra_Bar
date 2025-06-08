from django.urls import path
from .views import create_all_forms, success_page, search_page, print_page

urlpatterns = [
    path('issuance/', create_all_forms, name='form'),
    path('success/', success_page, name='success'),
    path('search/', search_page, name='search'),
    path('print/', print_page, name='print'),
]
