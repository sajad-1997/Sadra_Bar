from django.urls import path
from .views import *
from . import views


urlpatterns = [
    path('issuance/', create_all_forms, name='form'),
    path('success/', success_page, name='success'),
    path('search/', search_page, name='search'),
    path('print/', print_page, name='print'),
    path('add-sender/', add_sender, name='add_sender'),
    path('add-receiver/', add_receiver, name='add_receiver'),
    path('add-driver/', add_driver, name='add_driver'),
    path('add-vehicle/', add_vehicle, name='add_vehicle'),
    path('search/', views.search_receiver, name='search_receiver'),
    path('ajax/search-keyboard/', views.search_receiver, name='search_receiver_keyboard'),

]
