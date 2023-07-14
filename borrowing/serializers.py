from rest_framework import serializers

from book.serializers import BookSerializer
from payment.models import Payment
from payment.serializers import PaymentSerializer
from .models import Borrowing


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
