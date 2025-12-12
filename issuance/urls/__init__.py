from django.urls import path, include

urlpatterns = [
    path('manager/', include('issuance.urls.manager_urls')),
]
