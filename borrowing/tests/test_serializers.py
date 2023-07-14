from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
)
from payment.models import Payment


class BorrowingSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "password")
        self.book = Book.objects.create(
            title="Test Book",
            daily_fee=10.0,
            inventory=5,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=date(2023, 1, 1),
            expected_return_date=date(2023, 1, 5),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        self.serializer = BorrowingSerializer(instance=self.borrowing)

    def test_serializer_fields(self):
        expected_fields = {
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        }
        self.assertEqual(set(self.serializer.data.keys()), expected_fields)

    def test_validate_method_with_pending_payments(self):
        Payment.objects.create(
            borrowing=self.borrowing,
            status=Payment.StatusChoices.PENDING,
            money_to_pay=self.book.daily_fee,
        )
        context = {"request": self.client.get("/")}
        serializer = BorrowingSerializer(
            instance=self.borrowing, context=context, data=self.borrowing
        )

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_book_method_with_zero_inventory(self):
        self.book.inventory = 0
        self.book.save()
        validated_data = {"book": self.book}
        serializer = BorrowingSerializer(data=validated_data)

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)


class BorrowingListSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "password")
        self.book = Book.objects.create(
            title="Test Book",
            daily_fee=10.0,
            inventory=5,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=date(2023, 1, 1),
            expected_return_date=date(2023, 1, 5),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        self.serializer = BorrowingListSerializer(instance=self.borrowing)

    def test_serializer_fields(self):
        expected_fields = {
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        }
        self.assertEqual(set(self.serializer.data.keys()), expected_fields)


class BorrowingReturnSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "password")
        self.book = Book.objects.create(
            title="Test Book",
            daily_fee=10.0,
            inventory=5,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=date(2023, 1, 1),
            expected_return_date=date(2023, 1, 5),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        self.serializer = BorrowingReturnSerializer(instance=self.borrowing)

    def test_serializer_fields(self):
        expected_fields = {
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        }
        self.assertEqual(set(self.serializer.data.keys()), expected_fields)

    def test_validate_method_with_already_returned_book(self):
        self.borrowing.actual_return_date = date.today()
        self.borrowing.save()
        validated_data = {}
        serializer = BorrowingReturnSerializer(
            instance=self.borrowing, data=validated_data
        )

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
