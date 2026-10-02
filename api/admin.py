from django.contrib import admin
from .models import ContactMessage, DiplomatInquiry, AcademyEnrollment


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')


@admin.register(DiplomatInquiry)
class DiplomatInquiryAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')


@admin.register(AcademyEnrollment)
class AcademyEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'course_title',
                    'payment_status', 'created_at')
    list_filter = ('payment_status', 'course_title')
    search_fields = ('full_name', 'mpesa_phone_number', 'checkout_request_id')
