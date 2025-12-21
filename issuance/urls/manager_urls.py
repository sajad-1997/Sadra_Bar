from django.urls import path

from issuance.views.manager.approval import send_for_approval, approve_bijak, reject_bijak
from issuance.views.manager.manager_preview import manager_preview_page
from issuance.views.manager.print import bijak_print
from issuance.views.manager.review_pending_list import waiting_list

app_name = 'manager'

urlpatterns = [
    # مدیر
    path('waiting/', waiting_list, name='waiting_list'),
    path('bijak/<int:pk>/preview/', manager_preview_page, name="preview"),
    path('<int:bijak_id>/send/', send_for_approval, name='send_for_approval'),
    path('<int:bijak_id>/approve/', approve_bijak, name='approve_bijak'),
    path('<int:bijak_id>/reject/', reject_bijak, name='reject_bijak'),

    # چاپ بارنامه
    path('<int:bijak_id>/print/', bijak_print, name='bijak_print'),
]
