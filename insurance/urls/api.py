from rest_framework import routers
from rest_framework.routers import DefaultRouter
from insurance.views.api import *
from insurance.views.upload import UploadInsuranceInvoicePDF

from django.urls import path

router = routers.DefaultRouter()
router.register(r'companies', InsuranceCompanyViewSet)
router.register(r'contracts', InsuranceContractViewSet)
router.register(r'policy-types', InsurancePolicyTypeViewSet)
router.register(r'policies', InsurancePolicyViewSet)
router.register(r'invoices', InsuranceInvoiceViewSet)
router.register(r'commissions', InsuranceCommissionAllocationViewSet)
router.register(r'payments', InsurancePaymentTrackingViewSet)
router.register(r'alerts', InsuranceAlertViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('dashboard/', InsuranceDashboardAPIView.as_view(), name='insurance-dashboard'),
    path('upload-invoice-pdf/', UploadInsuranceInvoicePDF.as_view(), name='upload-invoice-pdf'),

]