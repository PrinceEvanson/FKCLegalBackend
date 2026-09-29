from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    number = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class DiplomatInquiry(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    number = models.CharField(max_length=50, blank=True, null=True)
    diplomatic_status = models.CharField(max_length=100, blank=True, null=True)
    mission_or_country = models.CharField(
        max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'Diplomatic Inquiry'}"


class AcademyEnrollment(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    email = models.EmailField()
    course_title = models.CharField(max_length=255)
    tuition_fee = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50)
    mpesa_phone_number = models.CharField(max_length=50, blank=True, null=True)
    checkout_request_id = models.CharField(
        max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.course_title} ({self.payment_status})"
