import stripe
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.telegram_helper import send_telegram_message
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user=self.request.user)

        return queryset

    @action(detail=True, methods=["GET"], url_path="success")
    def payment_success(self, request, pk=None):
        """Handle a successful payment"""
        payment = get_object_or_404(Payment, pk=pk)

        session = stripe.checkout.Session.retrieve(payment.session_id)
        if session.payment_status == "paid":
            payment.status = Payment.status.PAID
            payment.save()

            message = (
                f"Payment #{payment.id} was successful.\n"
                f"Type: {payment.type}\n"
                f"Borrowing: {payment.borrowing}"
            )
            send_telegram_message(message)

            return Response(
                {"success": "Payment was successful."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Payment was not successful."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["GET"], url_path="cancel")
    def payment_cancel(self, request, pk=None):
        """Handle a canceled payment"""
        return Response(
            {"message": "Payment can be made later."},
            status=status.HTTP_200_OK,
        )
