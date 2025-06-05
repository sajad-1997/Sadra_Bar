from django.urls import path
from .views import index, tariff

urlpatterns = [
    path('', index, name='index'),
    path('tariff/', tariff, name='tariff'),
]