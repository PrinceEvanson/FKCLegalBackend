from rest_framework import generics, status, views
from rest_framework.response import Response
from .models import ContactMessage, DiplomatInquiry, AcademyEnrollment
from .serializers import (
    ContactMessageSerializer,
    DiplomatInquirySerializer,
    AcademyEnrollmentSerializer
)
from .utils import initiate_stk_push


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
