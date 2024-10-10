# library_management_system/transactions/tasks.py

from celery import shared_task
from .models import Transaction
from django.utils import timezone

@shared_task(bind=True)
def check_overdue_books():
    """
    Periodically checks for overdue books and sends notifications.
    """
    overdue_transactions = Transaction.objects.filter(is_returned=False, due_date__lt=timezone.now())
    
    for transaction in overdue_transactions:
        transaction.send_overdue_notification()