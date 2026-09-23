from rest_framework import generics, status
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

                return Response({
                    "success": True,
                    "message": "Enrollment saved. M-Pesa STK push sent to your phone.",
                    "enrollment": serializer.data,
                    "stk_response": stk_response
                }, status=status.HTTP_201_CREATED)

        return Response({
            "success": True,
            "message": "Enrollment saved successfully.",
            "enrollment": serializer.data
        }, status=status.HTTP_201_CREATED)
