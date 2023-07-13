from django_q.tasks import async_task
from datetime import date, timedelta
from .models import Borrowing
from .telegram_helper import send_telegram_message


def check_overdue_borrowings():
    tomorrow = date.today() + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow,
        actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user_email = borrowing.user.email
            book_title = borrowing.book.title
            message = f"Borrowing overdue:\nUser: {user_email}\nBook: {book_title}"
            send_telegram_message(message)
    else:
        message = "No borrowings overdue today!"
        send_telegram_message(message)


async_task(check_overdue_borrowings)
