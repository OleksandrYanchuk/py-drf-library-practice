from django.db import transaction
from rest_framework import serializers

from book.serializers import BookSerializer
from .models import Borrowing
from .telegram_helper import send_telegram_message


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")

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
