from django.db.models import Sum
from rest_framework import viewsets, APIView, Response

from insurance.serializers.serializers import *


class InsuranceCompanyViewSet(viewsets.ModelViewSet):
    queryset = InsuranceCompany.objects.all()
    serializer_class = InsuranceCompanySerializer


class InsuranceContractViewSet(viewsets.ModelViewSet):
    queryset = InsuranceContract.objects.all()
    serializer_class = InsuranceContractSerializer


class InsurancePolicyTypeViewSet(viewsets.ModelViewSet):
    queryset = InsurancePolicyType.objects.all()
    serializer_class = InsurancePolicyTypeSerializer


class InsurancePolicyViewSet(viewsets.ModelViewSet):
    queryset = InsurancePolicy.objects.all()
    serializer_class = InsurancePolicySerializer


class InsuranceInvoiceViewSet(viewsets.ModelViewSet):
    queryset = InsuranceInvoice.objects.all()
    serializer_class = InsuranceInvoiceSerializer


class InsuranceCommissionAllocationViewSet(viewsets.ModelViewSet):
    queryset = InsuranceCommissionAllocation.objects.all()
    serializer_class = InsuranceCommissionAllocationSerializer


class InsurancePaymentTrackingViewSet(viewsets.ModelViewSet):
    queryset = InsurancePaymentTracking.objects.all()
    serializer_class = InsurancePaymentTrackingSerializer


class InsuranceAlertViewSet(viewsets.ModelViewSet):
    queryset = InsuranceAlert.objects.all()
    serializer_class = InsuranceAlertSerializer


class InsuranceDashboardAPIView(APIView):
    def get(self, request):
        # بدهی کل
        total_debt = InsuranceInvoice.objects.aggregate(
            total_amount=Sum('total_amount')
        )['total_amount'] or 0

        # بدهی پرداخت شده
        total_paid = InsurancePaymentTracking.objects.aggregate(
            total_paid=Sum('paid_amount')
        )['total_paid'] or 0

        # مانده بدهی
        remaining_debt = total_debt - total_paid

        # تعداد بیمه‌ها
        policies_count = InsurancePolicy.objects.count()

        # تعداد هشدارها
        alerts_count = InsuranceAlert.objects.filter(status='pending').count()

        # تخصیص کمیسیون کل
        total_commission_allocated = InsuranceCommissionAllocation.objects.aggregate(
            total_allocated=Sum('allocated_amount')
        )['total_allocated'] or 0

        return Response({
            'total_debt': total_debt,
            'total_paid': total_paid,
            'remaining_debt': remaining_debt,
            'policies_count': policies_count,
            'alerts_count': alerts_count,
            'total_commission_allocated': total_commission_allocated
        })
