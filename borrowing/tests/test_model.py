from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing

BORROWING_URL = reverse("borrowings:borrowing-list")


class BorrowingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "password")
        self.book = Book.objects.create(
            title="Test Book",
            daily_fee=10.0,
            inventory=5,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.now().date(),
            expected_return_date=datetime.now().date(),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        self.client.force_authenticate(self.user)

    def test_str_method(self):
        self.assertEqual(str(self.borrowing), "user@user.com: Test Book")

    def test_total_price(self):
        self.assertEqual(self.borrowing.total_price, 10.0)

    def test_fine_price_property(self):
        self.assertEqual(self.borrowing.fine_price, 10.0)
