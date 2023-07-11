from django.db import models


class PaymentStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'


class PaymentTypeChoices(models.TextChoices):
    PAYMENT = 'PAYMENT', 'Payment'
    FINE = 'FINE', 'Fine'
