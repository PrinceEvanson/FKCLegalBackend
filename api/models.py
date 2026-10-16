from django.contrib.auth.models import User
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    number = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    fulfillment_status = models.CharField(max_length=50, default="Incomplete")
    payment_status = models.CharField(max_length=50, default="Pending")
    price = models.CharField(max_length=50, default="1,000")
    price_set = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    read_by = models.CharField(max_length=150, blank=True, default="")
    # Append-only log of daily progress notes: [{"text", "author", "at"}, ...]
    updates = models.JSONField(default=list, blank=True)
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
    fulfillment_status = models.CharField(max_length=50, default="Incomplete")
    payment_status = models.CharField(max_length=50, default="Pending")
    price = models.CharField(max_length=50, default="1,000")
    price_set = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    read_by = models.CharField(max_length=150, blank=True, default="")
    # Append-only log of daily progress notes: [{"text", "author", "at"}, ...]
    updates = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'Diplomatic Inquiry'}"


class FoundationRequest(models.Model):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField()
    number = models.CharField(max_length=50, blank=True, null=True)
    message = models.TextField()
    fulfillment_status = models.CharField(max_length=50, default="Incomplete")
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    read_by = models.CharField(max_length=150, blank=True, default="")
    updates = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PartnerInquiry(FoundationRequest):
    partnership_type = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.name} - {self.partnership_type or 'Foundation Partnership'}"


class CommunityProjectProposal(FoundationRequest):
    project_title = models.CharField(max_length=255, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    beneficiaries = models.CharField(max_length=255, blank=True, default="")
    budget_estimate = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.name} - {self.project_title}"


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


class AdminActivityLog(models.Model):
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin.username} - {self.action} at {self.timestamp}"


class AdminStatus(models.Model):
    admin = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='status')
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.username} - Last active: {self.last_active}"
