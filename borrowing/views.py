import os

import stripe
from django.db import transaction
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.models import Payment
from payment.payment_service import create_stripe_session
from .models import Borrowing
from .permissions import IsOwnerOrAdmin
from .serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
)
from .telegram_helper import send_telegram_message

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["user__email", "book__title"]  # Add additional fields for search
    ordering_fields = [
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    ]  # Add additional fields for ordering

    def get_queryset(self):
        user = self.request.user
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)

        if user.is_superuser:
            borrowings = Borrowing.objects.all()
            if is_active is not None and is_active.lower() == "true":
                borrowings = borrowings.filter(actual_return_date__isnull=True)
            if user_id is not None:
                borrowings = borrowings.filter(user_id=user_id)
            return borrowings
        elif user.is_authenticated:
            borrowings = Borrowing.objects.filter(user=user)
            if is_active is not None and is_active.lower() == "true":
                borrowings = borrowings.filter(actual_return_date__isnull=True)
            return borrowings
        else:
            return Borrowing.objects.none()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer

        if self.action == "book_return":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.validated_data["book"]
        user = request.user

        borrowing = Borrowing.objects.create(
            expected_return_date=serializer.data["expected_return_date"],
            book=book,
            user=user,
        )

        create_stripe_session(request, borrowing)
        if book.inventory == 0:
            return Response(
                {"detail": "Book is not available for borrowing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        book.inventory -= 1
        book.save()

        headers = self.get_success_headers(serializer.data)
        message = f"New borrowing created:\nUser: {user.email}\nBook: {book.title}"
        send_telegram_message(message)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("You are not authorized to access this resource.")

        return super().list(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if borrowing is already returned
        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "Borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.now().date()
        borrowing.save()

        # Increase book inventory by 1
        book = serializer.validated_data["book"]
        book.inventory += 1
        book.save()

        serializer = self.get_serializer(borrowing)
        if borrowing.actual_return_date > borrowing.expected_return_date:
            fine_amount = borrowing.fine_price

            Payment.objects.create(
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.FINE,
                borrowing=borrowing,
                money_to_pay=fine_amount,
            )

        return Response(serializer.data)
