from rest_framework import serializers
from .models import ContactMessage, DiplomatInquiry, AcademyEnrollment


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'


class DiplomatInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiplomatInquiry
        fields = '__all__'


class AcademyEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademyEnrollment
        fields = '__all__'
