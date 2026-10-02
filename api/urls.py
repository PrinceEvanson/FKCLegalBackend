from django.urls import path
from .views import (
    ContactCreateView,
    ContactUpdateView,
    DiplomatUpdateView,
    DiplomatCreateView,
    AcademyEnrollmentCreateView,
    MpesaCallbackView,
    PaymentStatusView,
    AdminDashboardDataView,
    AdminUpdateCredentialsView
)

urlpatterns = [
    path('contact/', ContactCreateView.as_view(), name='contact-create'),
    path('diplomat/', DiplomatCreateView.as_view(), name='diplomat-create'),
    path('academy-enroll/', AcademyEnrollmentCreateView.as_view(),
         name='academy-enroll'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('mpesa/status/<str:checkout_request_id>/',
         PaymentStatusView.as_view(), name='payment-status'),
    path('admin/dashboard-data/', AdminDashboardDataView.as_view(),
         name='admin-dashboard-data'),
    path('admin/update-credentials/', AdminUpdateCredentialsView.as_view(),
         name='admin-update-credentials'),
    path('admin/contacts/<int:pk>/update/', ContactUpdateView.as_view(),
         name='contact-update'),
    path('admin/diplomats/<int:pk>/update/', DiplomatUpdateView.as_view(),
         name='diplomat-update'),
]
