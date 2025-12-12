from django.urls import path
from issuance.views.approval import send_for_approval, approve_bijak, reject_bijak
from issuance.views.manager import waiting_list

urlpatterns = [
    path("waiting/", waiting_list, name="manager_waiting_list"),
    path("<int:bijak_id>/send/", send_for_approval, name="send_for_approval"),
    path("<int:bijak_id>/approve/", approve_bijak, name="approve_bijak"),
    path("<int:bijak_id>/reject/", reject_bijak, name="reject_bijak"),
]
