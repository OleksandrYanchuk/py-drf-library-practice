from datetime import date

from django.db import IntegrityError
from django.test import TestCase

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from user.models import User


class PaymentModelTestCase(TestCase):
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

    def test_create_payment(self):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="123456789",
            money_to_pay=10.0,
        )
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.type, Payment.TypeChoices.PAYMENT)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.session_url, "https://example.com")
        self.assertEqual(payment.session_id, "123456789")
        self.assertEqual(payment.money_to_pay, 10.0)

    def test_payment_str(self):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PAID,
            type=Payment.TypeChoices.FINE,
            borrowing=self.borrowing,
            session_url="https://example.com",
            session_id="987654321",
            money_to_pay=5.0,
        )
        self.assertEqual(str(payment), "Payment #{}".format(payment.id))

    def test_payment_borrowing_foreign_key(self):
        # Creating a payment without a borrowing should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                status=Payment.StatusChoices.PENDING,
                type=Payment.TypeChoices.PAYMENT,
                session_url="https://example.com",
                session_id="123456789",
                money_to_pay=10.0,
            )
