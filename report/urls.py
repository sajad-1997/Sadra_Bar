# report/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    # path('export/pdf/', views.export_pdf, name='report_export_pdf'),
    # path('export/excel/', views.export_excel, name='report_export_excel'),
]
