# Generated by Django 4.0.4 on 2023-07-12 08:54

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("book", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("borrowing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="book",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to="book.book",
            ),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="borrow_date",
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="expected_return_date",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
