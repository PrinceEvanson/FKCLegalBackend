from django.urls import path
from .views import (
    ContactCreateView,
    DiplomatCreateView,
    AcademyEnrollmentCreateView,
    MpesaCallbackView,
    PaymentStatusView
)

urlpatterns = [
    path('contact/', ContactCreateView.as_view(), name='contact-create'),
    path('diplomat/', DiplomatCreateView.as_view(), name='diplomat-create'),
    path('academy-enroll/', AcademyEnrollmentCreateView.as_view(),
         name='academy-enroll'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('mpesa/status/<str:checkout_request_id>/',
         PaymentStatusView.as_view(), name='payment-status'),
]
