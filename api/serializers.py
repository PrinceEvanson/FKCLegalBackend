import re

from django.conf import settings
from rest_framework import serializers

from .models import ContactMessage, DiplomatInquiry, AcademyEnrollment


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        
        read_only_fields = (
            'fulfillment_status',
            'payment_status',
            'price',
            'price_set',
            'fulfilled_at',
            'created_at',
        )

    def validate_subject(self, value):
        """Only accept a real service title (or "Other") from the public form."""
        value = value.strip()
        allowed = [*getattr(settings, 'ALLOWED_CONTACT_SUBJECTS', []), 'Other']
        
        if len(allowed) == 1:
            return value
        lookup = {s.lower(): s for s in allowed}
        canonical = lookup.get(value.lower())
        if canonical is None:
            raise serializers.ValidationError(
                'Please choose a service from the list.')
        return canonical

    def validate_number(self, value):
        if not value:
            return value
        cleaned = re.sub(r'[\s\-().]', '', value)
        if not re.fullmatch(r'\+?\d{9,15}', cleaned):
            raise serializers.ValidationError(
                'Enter a valid phone number, e.g. 0712345678.')
        return cleaned

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                'Please describe your request in a little more detail.')
        return value


class DiplomatInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiplomatInquiry
        fields = '__all__'
        
        read_only_fields = (
            'fulfillment_status',
            'payment_status',
            'price',
            'price_set',
            'fulfilled_at',
            'created_at',
        )


class AcademyEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademyEnrollment
        fields = '__all__'
        
        read_only_fields = (
            'payment_status',
            'checkout_request_id',
            'created_at',
        )
