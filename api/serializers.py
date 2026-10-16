import re

from django.conf import settings
from rest_framework import serializers

from .models import (
    AcademyEnrollment,
    CommunityProjectProposal,
    ContactMessage,
    DiplomatInquiry,
    PartnerInquiry,
)


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        # Admin-managed fields: the public contact form must not be able to set these.
        read_only_fields = (
            'fulfillment_status',
            'payment_status',
            'price',
            'price_set',
            'fulfilled_at',
            'is_read',
            'read_at',
            'read_by',
            'updates',
            'created_at',
        )

    def validate_subject(self, value):
        """Only accept a real service title (or "Other") from the public form."""
        value = value.strip()
        allowed = [*getattr(settings, 'ALLOWED_CONTACT_SUBJECTS', []), 'Other']
        # If ALLOWED_CONTACT_SUBJECTS isn't configured yet, only "Other" would be
        # allowed, so skip the check until the list is filled in.
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
        # Admin-managed fields: the public diplomat form must not be able to set these.
        read_only_fields = (
            'fulfillment_status',
            'payment_status',
            'price',
            'price_set',
            'fulfilled_at',
            'is_read',
            'read_at',
            'read_by',
            'updates',
            'created_at',
        )


class AcademyEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademyEnrollment
        fields = '__all__'
        # Payment state is set only by the server / M-Pesa callback, never by the client.
        read_only_fields = (
            'payment_status',
            'checkout_request_id',
            'created_at',
        )


FOUNDATION_READ_ONLY = (
    'fulfillment_status',
    'fulfilled_at',
    'is_read',
    'read_at',
    'read_by',
    'updates',
    'created_at',
)


class PartnerInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerInquiry
        fields = '__all__'
        read_only_fields = FOUNDATION_READ_ONLY

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                'Please tell us a little more about how you would like to help.')
        return value

    def validate_number(self, value):
        if not value:
            return value
        cleaned = re.sub(r'[\s\-().]', '', value)
        if not re.fullmatch(r'\+?\d{9,15}', cleaned):
            raise serializers.ValidationError(
                'Enter a valid phone number, e.g. 0712345678.')
        return cleaned


class CommunityProjectProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityProjectProposal
        fields = '__all__'
        read_only_fields = FOUNDATION_READ_ONLY

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                'Please describe the project in a little more detail.')
        return value

    def validate_number(self, value):
        if not value:
            return value
        cleaned = re.sub(r'[\s\-().]', '', value)
        if not re.fullmatch(r'\+?\d{9,15}', cleaned):
            raise serializers.ValidationError(
                'Enter a valid phone number, e.g. 0712345678.')
        return cleaned
