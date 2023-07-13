from django.db import transaction
from django.utils import timezone, dateformat
from rest_framework import serializers, status
from rest_framework.response import Response

from book.serializers import BookSerializer
from payment.models import Payment
from payment.payment_service import create_stripe_session
from payment.serializers import PaymentSerializer
from .models import Borrowing
from .telegram_helper import send_telegram_message


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")

        def validate(self, attrs):
            user = self.context["request"].user

            if Payment.objects.filter(
                    borrowing__user=user, status=Payment.StatusChoices.PENDING
            ).exists():
                raise serializers.ValidationError(
                    "You have pending payments. Cannot borrow a new book."
                )

        @staticmethod
        def validate_book(self, book):
            if book.inventory == 0:
                raise serializers.ValidationError(
                    "Book is not available for borrowing."
                )
            return book

        @transaction.atomic
        def create(self, validated_data):
            book = validated_data["book"]
            user = self.context["request"].user

            borrowing = Borrowing.objects.create(
                expected_return_date=validated_data["expected_return_date"],
                book=book,
                user=user,
            )

            create_stripe_session(self.context["request"], borrowing)

            book.inventory -= 1
            book.save()

            message = (
                f"New borrowing created:\nUser: {user.email}\nBook: {book.title}"
            )
            send_telegram_message(message)

            return borrowing


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.ReadOnlyField(source="user.email")


class BorrowingReturnSerializer(BorrowingSerializer):
    expected_return_date = serializers.ReadOnlyField()
    book = serializers.ReadOnlyField()

    def validate(self, attrs):
        borrowing = self.instance

        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError("Book has already been returned")

        return attrs
