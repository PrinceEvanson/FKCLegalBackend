import ipaddress
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import (
    AcademyEnrollment,
    AdminActivityLog,
    AdminStatus,
    ContactMessage,
    DiplomatInquiry,
)
from .serializers import (
    AcademyEnrollmentSerializer,
    ContactMessageSerializer,
    DiplomatInquirySerializer,
)
from .utils import initiate_stk_push

VALID_FULFILLMENT_STATUSES = {"Incomplete", "Fulfilled"}
VALID_PAYMENT_STATUSES = {"Pending", "Completed"}
MIN_PRICE = 1000


def get_client_ip(request):
    """Best-effort client IP (works behind ngrok / proxies). Returns None if invalid."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    raw = forwarded.split(",")[0].strip(
    ) if forwarded else request.META.get("REMOTE_ADDR")
    try:
        return str(ipaddress.ip_address(raw))
    except (ValueError, TypeError):
        return None


class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer


class DiplomatCreateView(generics.CreateAPIView):
    queryset = DiplomatInquiry.objects.all()
    serializer_class = DiplomatInquirySerializer


class AcademyEnrollmentCreateView(generics.CreateAPIView):
    queryset = AcademyEnrollment.objects.all()
    serializer_class = AcademyEnrollmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()

        payment_method = str(enrollment.payment_method).lower()
        if "m-pesa" in payment_method or "mpesa" in payment_method:
            phone = enrollment.mpesa_phone_number
            if phone:
                if phone.startswith('0'):
                    phone = '254' + phone[1:]
                elif phone.startswith('+'):
                    phone = phone[1:]

                raw_fee = str(enrollment.tuition_fee or "50000")
                amount = ''.join(filter(str.isdigit, raw_fee))
                if not amount:
                    amount = "50000"

                stk_response = initiate_stk_push(
                    phone_number=phone,
                    amount=amount,
                    account_reference="FKC Academy",
                    description=f"Enrollment: {enrollment.course_title}"
                )

                if hasattr(stk_response, 'json'):
                    stk_data = stk_response.json()
                elif isinstance(stk_response, dict):
                    stk_data = stk_response
                else:
                    stk_data = {}

                checkout_id = (
                    stk_data.get("CheckoutRequestID") or
                    stk_data.get("checkoutRequestID") or
                    stk_data.get("data", {}).get("CheckoutRequestID")
                )

                if checkout_id:
                    enrollment.checkout_request_id = checkout_id
                    enrollment.payment_status = "Pending"
                    enrollment.save()

                return Response({
                    "success": True,
                    "message": "STK push initiated. Waiting for payment confirmation.",
                    "enrollment": serializer.data,
                    "checkout_request_id": checkout_id,
                    "stk_response": stk_data
                }, status=status.HTTP_201_CREATED)

        return Response({
            "success": True,
            "message": "Enrollment saved successfully.",
            "enrollment": serializer.data
        }, status=status.HTTP_201_CREATED)


class MpesaCallbackView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")

            enrollment = AcademyEnrollment.objects.filter(
                checkout_request_id=checkout_id).first()
            if enrollment:
                if result_code == 0:
                    enrollment.payment_status = "Completed"
                else:
                    enrollment.payment_status = "Failed"
                enrollment.save()

        except Exception as e:
            return Response({"resultCode": 1, "resultDesc": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"resultCode": 0, "resultDesc": "Accepted"})


class PaymentStatusView(views.APIView):
    def get(self, request, checkout_request_id, *args, **kwargs):
        enrollment = AcademyEnrollment.objects.filter(
            checkout_request_id=checkout_request_id).first()
        if not enrollment:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "checkout_request_id": enrollment.checkout_request_id,
            "payment_status": enrollment.payment_status
        })


class AdminDashboardDataView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        AdminStatus.objects.update_or_create(
            admin=request.user,
            defaults={'last_active': timezone.now()}
        )

        enrollments = AcademyEnrollmentSerializer(
            AcademyEnrollment.objects.all().order_by('-created_at'), many=True
        ).data
        contacts = ContactMessageSerializer(
            ContactMessage.objects.all().order_by('-created_at'), many=True
        ).data
        diplomats = DiplomatInquirySerializer(
            DiplomatInquiry.objects.all().order_by('-created_at'), many=True
        ).data

        # Activity logs are only ever sent to the 'dev' account.
        activity_logs = []
        if request.user.username == 'dev':
            three_mins_ago = timezone.now() - timedelta(minutes=3)

            logs_queryset = AdminActivityLog.objects.all(
            ).select_related('admin', 'admin__status')
            for log in logs_queryset:
                is_active = False
                if hasattr(log.admin, 'status') and log.admin.status.last_active:
                    is_active = log.admin.status.last_active >= three_mins_ago

                activity_logs.append({
                    'admin__username': log.admin.username,
                    'action': log.action,
                    'ip_address': log.ip_address,
                    'timestamp': log.timestamp,
                    'is_active': is_active
                })

        return Response({
            "username": request.user.username,
            "enrollments": enrollments,
            "contacts": contacts,
            "diplomats": diplomats,
            "activity_logs": activity_logs
        })


class InquiryUpdateView(views.APIView):
    """Shared admin PATCH logic for contact and diplomat inquiries."""
    permission_classes = [IsAdminUser]
    model = None
    serializer_class = None
    label = "inquiry"

    def patch(self, request, pk, *args, **kwargs):
        try:
            obj = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({"error": "Inquiry not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        changes = []

        if "fulfillment_status" in data:
            value = data["fulfillment_status"]
            if value not in VALID_FULFILLMENT_STATUSES:
                return Response(
                    {"error": f"fulfillment_status must be one of: {', '.join(sorted(VALID_FULFILLMENT_STATUSES))}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if value != obj.fulfillment_status:
                changes.append(
                    f"fulfillment {obj.fulfillment_status} -> {value}")
            obj.fulfillment_status = value
            if value == "Fulfilled" and not obj.fulfilled_at:
                obj.fulfilled_at = timezone.now()
            elif value == "Incomplete":
                obj.fulfilled_at = None

        if "payment_status" in data:
            value = data["payment_status"]
            if value not in VALID_PAYMENT_STATUSES:
                return Response(
                    {"error": f"payment_status must be one of: {', '.join(sorted(VALID_PAYMENT_STATUSES))}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if value != obj.payment_status:
                changes.append(f"payment {obj.payment_status} -> {value}")
            obj.payment_status = value

        if "price" in data:
            digits = ''.join(ch for ch in str(
                data["price"]).split('.')[0] if ch.isdigit())
            if not digits or int(digits) < MIN_PRICE:
                return Response(
                    {"error": f"Price cannot be less than {MIN_PRICE:,} Ksh."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_price = f"{int(digits):,}"
            if new_price != obj.price:
                changes.append(f"price {obj.price} -> {new_price}")
            obj.price = new_price
            obj.price_set = True
        elif "price_set" in data:
            obj.price_set = data["price_set"] is True or str(
                data["price_set"]).lower() == "true"

        if not changes and "price_set" not in data:
            return Response({
                "success": True,
                "message": "No changes.",
                "inquiry": self.serializer_class(obj).data
            })

        obj.save()

        AdminActivityLog.objects.create(
            admin=request.user,
            action=f"Updated {self.label} #{obj.id} for client '{obj.name}'"
            + (f": {'; '.join(changes)}" if changes else ""),
            ip_address=get_client_ip(request)
        )

        return Response({
            "success": True,
            "message": "Inquiry updated successfully.",
            "inquiry": self.serializer_class(obj).data
        })


class ContactUpdateView(InquiryUpdateView):
    model = ContactMessage
    serializer_class = ContactMessageSerializer
    label = "inquiry"


class DiplomatUpdateView(InquiryUpdateView):
    model = DiplomatInquiry
    serializer_class = DiplomatInquirySerializer
    label = "diplomat inquiry"


class AdminUpdateCredentialsView(views.APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        user = request.user
        new_username = request.data.get("username")
        new_password = request.data.get("password")

        if not new_username and not new_password:
            return Response(
                {"success": False, "message": "Provide a new username and/or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        changes = []
        if new_username:
            new_username = new_username.strip()
            if User.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
                return Response(
                    {
                        "success": False,
                        "message": "A user with this username already exists (case-insensitive match)."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.username = new_username
            changes.append("username")

        if new_password:
            try:
                validate_password(new_password, user=user)
            except DjangoValidationError as exc:
                return Response(
                    {"success": False, "message": " ".join(exc.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
            changes.append("password")

        user.save()

        AdminActivityLog.objects.create(
            admin=user,
            action=f"Updated admin credentials: {', '.join(changes)}",
            ip_address=get_client_ip(request)
        )

        return Response({"success": True, "message": "Credentials updated successfully."})
