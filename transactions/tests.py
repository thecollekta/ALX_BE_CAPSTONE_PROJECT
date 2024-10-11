# library_management_system/transactions/tests.py

from django.test import TestCase
from django.utils import timezone
from .models import Book, Transaction
from accounts.models import CustomUser

# Test for Transaction Model
class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", 
            password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date=timezone.now(),
            available_copies=5
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            check_out_date=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=14)
        )