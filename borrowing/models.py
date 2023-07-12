from django.db import models

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="borrowings"
    )

    def __str__(self):
        return f"{self.user.email}: {self.book.title}"

    @property
    def total_price(self):
        return (
                self.book.daily_fee
                * (self.expected_return_date - self.borrow_date).days
        )

    @property
    def fine_price(self):
        return (
                self.book.daily_fee
                * (self.actual_return_date - self.expected_return_date).days
        ) * 2
