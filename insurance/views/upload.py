from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from insurance.models.attachment import InsuranceInvoiceAttachment
from insurance.utils.pdf_invoice_parser import parse_insurance_invoice


class UploadInsuranceInvoicePDF(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "فایل ارسال نشده"}, status=status.HTTP_400_BAD_REQUEST)

        # ذخیره فایل PDF
        attachment = InsuranceInvoiceAttachment.objects.create(file=file_obj)

        # پردازش PDF و ایجاد رکورد Invoice و کمیسیون
        try:
            invoice = parse_insurance_invoice(attachment.file.path)
            attachment.invoice = invoice
            attachment.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "PDF پردازش شد و اطلاعات ثبت شد", "invoice_id": invoice.id})
