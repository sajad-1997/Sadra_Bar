from django.urls import path
from .views import *

# from . import views

urlpatterns = [
    path('create_new/', create_new, name='create_new'),
    path('success/', success_page, name='success'),
    path('search/', search_page, name='search'),
    path('print/', bijak_last_view, name='print'),
    path('preview/<int:pk>/', preview_page, name='preview'),

    # path('add-sender/', add_sender, name='add_sender'),
    path('add-customer/', add_customer, name='add_customer'),
    path('add-driver/', add_driver, name='add_driver'),
    path('add-vehicle/', add_vehicle, name='add_vehicle'),

    # path('edit-sender/', edit_sender, name='edit_sender'),
    path('edit-customer/', edit_customer, name='edit_customer'),
    path('edit-driver/', edit_driver, name='edit_driver'),
    path('edit-vehicle/', edit_vehicle, name='edit_vehicle'),
    path('edit-cargo/', edit_cargo, name='edit_cargo'),
    path('edit-bijak/', edit_bijak, name='edit_bijak'),

    path('search/customer/', search_customer, name='search_customer'),
    path('search/driver/', search_driver, name='search_driver'),
    path('search/vehicle/', search_vehicle, name='search_vehicle'),
    path('search/shipments/', search_shipment, name='search_shipment'),

    path("save-sender/", save_customer, name="save_customer"),
    path("save-driver/", save_driver, name="save_driver"),
    path('ajax/search-keyboard/', search_customer, name='search_customer_keyboard'),
    path("ajax/get-vehicle/", get_vehicle_by_driver, name="get_vehicle_by_driver"),

]
