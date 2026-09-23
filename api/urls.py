from django.urls import path
from .views import ContactCreateView, DiplomatCreateView, AcademyEnrollmentCreateView

urlpatterns = [
    path('contact/', ContactCreateView.as_view(), name='contact-create'),
    path('diplomat/', DiplomatCreateView.as_view(), name='diplomat-create'),
    path('academy-enroll/', AcademyEnrollmentCreateView.as_view(),
         name='academy-enroll'),
]
