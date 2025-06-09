from django.urls import path
from .views import create_all_forms, success_page, search_page, print_page, add_sender, add_receiver

urlpatterns = [
    path('issuance/', create_all_forms, name='form'),
    path('success/', success_page, name='success'),
    path('search/', search_page, name='search'),
    path('print/', print_page, name='print'),
    path('add-sender/', add_sender, name='add_sender'),
    path('add-receiver/', add_receiver, name='add_receiver'),

]
