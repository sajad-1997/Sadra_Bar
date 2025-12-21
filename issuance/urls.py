from django.urls import path, include

urlpatterns = [
    path('', include(('issuance.urls.crud_urls', 'crud'), namespace='crud')),
    path('', include(('issuance.urls.search_urls', 'search'), namespace='search')),
    path('', include(('issuance.urls.qr_urls', 'qr_code'), namespace='qr_code')),
    path('', include(('issuance.urls.bijak_approval_urls', 'bijak_approval'), namespace='bijak_approval')),

    path('manager/', include(('issuance.urls.manager_urls', 'manager'), namespace='manager')),
    path('report/', include(('report.urls', 'report'), namespace='report')),
]
