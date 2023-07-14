from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.models import User


class PaymentViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
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

    def test_list_payments(self):
        """Test retrieving a list of payments"""
        url = "/api/payment/payments/"

        response = self.client.get(url)
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_payment(self):
        """Test retrieving a single payment"""

        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="123456789",
            money_to_pay=10.0,
        )
        url = f"/api/payment/payments/{self.payment.pk}.json"
        response = self.client.get(url)
        serializer = PaymentSerializer(self.payment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
