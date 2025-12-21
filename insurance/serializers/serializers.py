from rest_framework import serializers

from insurance.models.alert import InsuranceAlert
from insurance.models.commission import InsuranceCommissionAllocation
from insurance.models.company import InsuranceCompany
from insurance.models.contract import InsuranceContract
from insurance.models.invoice import InsuranceInvoice
from insurance.models.payment import InsurancePaymentTracking
from insurance.models.policy import InsurancePolicy
from insurance.models.policy_type import InsurancePolicyType


class InsuranceCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCompany
        fields = '__all__'


class InsuranceContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceContract
        fields = '__all__'


class InsurancePolicyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePolicyType
        fields = '__all__'


class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePolicy
        fields = '__all__'


class InsuranceInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceInvoice
        fields = '__all__'


class InsuranceCommissionAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCommissionAllocation
        fields = '__all__'


class InsurancePaymentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePaymentTracking
        fields = '__all__'


class InsuranceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceAlert
        fields = '__all__'
