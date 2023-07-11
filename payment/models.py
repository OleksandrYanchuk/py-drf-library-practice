from django.db import models
from .choices import PaymentStatusChoices, PaymentTypeChoices
from borrowing.models import Borrowing


class Payment(models.Model):
    status = models.CharField(max_length=10, choices=PaymentStatusChoices.choices)
    type = models.CharField(max_length=10, choices=PaymentTypeChoices.choices)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
