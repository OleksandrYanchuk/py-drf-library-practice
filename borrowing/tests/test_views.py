from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from book.models import Book
from borrowing.models import Borrowing
from borrowing.views import BorrowingViewSet

User = get_user_model()


class BorrowingViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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

    def test_create_borrowing(self):
        url = "/api/borrowings/"
        data = {"expected_return_date": "2023-01-05", "book": self.book.id}
        request = self.factory.post(url, data)
        force_authenticate(request, user=self.user)

        view = BorrowingViewSet.as_view({"post": "create"})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)
        self.assertEqual(Borrowing.objects.last().user, self.user)

    def test_list_borrowings(self):
        url = "/api/borrowings/"
        request = self.factory.get(url)
        force_authenticate(request, user=self.user)

        view = BorrowingViewSet.as_view({"get": "list"})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_return_borrowing(self):
        url = f"/api/borrowings/{self.borrowing.id}/return/"
        data = {
            "expected_return_date": str(date.today()),
            "actual_return_date": str(date.today()),
            "book": self.book.id,
        }
        request = self.factory.post(url, data)
        force_authenticate(request, user=self.user)

        view = BorrowingViewSet.as_view({"post": "return_borrowing"})
        response = view(request, pk=self.borrowing.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["actual_return_date"], str(date.today()))
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_borrowing_already_returned(self):
        self.borrowing.actual_return_date = date.today()
        self.borrowing.save()

        url = f"/api/borrowings/{self.borrowing.id}/return/"
        data = {}
        request = self.factory.post(url, data)
        force_authenticate(request, user=self.user)

        view = BorrowingViewSet.as_view({"post": "return_borrowing"})
        response = view(request, pk=self.borrowing.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 5)
