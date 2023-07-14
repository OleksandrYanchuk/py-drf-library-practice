from datetime import datetime

from django.db import models

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self):
        return f"{self.user.email}: {self.book.title}"

    @property
    def total_price(self):
        borrow_date = datetime.strptime(str(self.borrow_date), "%Y-%m-%d").date()
        expected_return_date = datetime.strptime(
            str(self.expected_return_date), "%Y-%m-%d"
        ).date()

        if self.expected_return_date:
            return (
                    expected_return_date - borrow_date
            ).days * self.book.daily_fee + self.book.daily_fee

        return self.book.daily_fee

    @property
    def fine_price(self):
        if self.actual_return_date:
            actual_return_date = datetime.strptime(
                str(self.actual_return_date), "%Y-%m-%d"
            ).date()
            expected_return_date = datetime.strptime(
                str(self.expected_return_date), "%Y-%m-%d"
            ).date()
            return (
                    self.book.daily_fee * (actual_return_date - expected_return_date).days
            ) * 2
        return self.book.daily_fee
