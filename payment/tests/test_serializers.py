from datetime import date

from django.test import TestCase
from rest_framework import serializers

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.models import User


class PaymentSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.book = Book.objects.create(title="Test Book", daily_fee=10.0, inventory=5)

        self.borrowing = Borrowing.objects.create(
            borrow_date=date(2023, 1, 1),
            expected_return_date=date(2023, 1, 5),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="123456789",
            money_to_pay=10.0,
        )
        self.serializer = PaymentSerializer()

    def test_serializer_create_payment(self):
        """Test creating a new payment with the serializer"""
        data = {
            "status": self.payment.status,
            "type": self.payment.type,
            "borrowing": self.borrowing.id,
            "session_url": self.payment.session_url,
            "session_id": self.payment.session_id,
            "money_to_pay": self.payment.money_to_pay,
        }
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        self.assertEqual(payment.status, self.payment.status)
        self.assertEqual(payment.type, self.payment.type)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.session_url, self.payment.session_url)
        self.assertEqual(payment.session_id, self.payment.session_id)
        self.assertEqual(payment.money_to_pay, self.payment.money_to_pay)

    def test_serializer_update_payment(self):
        """Test updating a payment with the serializer"""
        updated_data = {
            "status": Payment.StatusChoices.PAID,
            "type": Payment.TypeChoices.FINE,
            "borrowing": self.borrowing.id,
            "session_url": "https://example.com/new",
            "session_id": "987654321",
            "money_to_pay": 15.0,
        }
        serializer = PaymentSerializer(self.payment, data=updated_data)
        serializer.is_valid(raise_exception=True)
        updated_payment = serializer.save()

        self.assertEqual(updated_payment.status, updated_data["status"])
        self.assertEqual(updated_payment.type, updated_data["type"])
        self.assertEqual(updated_payment.borrowing, self.borrowing)
        self.assertEqual(updated_payment.session_url, updated_data["session_url"])
        self.assertEqual(updated_payment.session_id, updated_data["session_id"])
        self.assertEqual(updated_payment.money_to_pay, updated_data["money_to_pay"])

    def test_serializer_invalid_money_to_pay(self):
        """Test that an invalid money_to_pay raises a validation error"""
        invalid_data = {
            "status": Payment.StatusChoices.PENDING,
            "type": Payment.TypeChoices.PAYMENT,
            "borrowing": self.borrowing,
            "session_url": "https://example.com",
            "session_id": "123456789",
            "money_to_pay": -10.0,
        }
        serializer = PaymentSerializer(data=invalid_data)

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
