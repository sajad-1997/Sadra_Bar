# 7️⃣ bijak_qr_views.py

from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from issuance.models import Bijak


# from .utils import num_to_word_rial


def bijak_qr(request, pk):
    bijak = get_object_or_404(Bijak, pk=pk)

    # لینک مقصد: صفحه چاپ بارنامه
    url = request.build_absolute_uri(f"/Barnameh/{pk}/print/")

    # تولید QR
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")
