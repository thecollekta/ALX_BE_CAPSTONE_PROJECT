# library_management_system/transactions/models.py

from django.db import models
from books.models import Book
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from accounts.tasks import send_email_async

User = get_user_model()

class Transaction(models.Model):
    """
    Model to track the check-out and return of books.
    Fields include:
        - user: ForeignKey to the user who checks out the book.
        - book: ForeignKey to the book being checked out.
        - checkout_date: Date when the book was checked out.
        - due_date: The date when the book is due (calculated automatically as 14 days from checkout).
        - return_date: Date when the book is returned.
        - is_returned: Boolean indicating if the book is returned.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    check_out_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=timezone.now() + timedelta(days=14))
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user']),  # For user lookups
            models.Index(fields=['book']),  # For book lookups
            models.Index(fields=['is_returned']),  # For filtering returned books
        ]

    def send_overdue_notification(self):
        """
        Sends an email notification to the user if the book is overdue.
        """
        subject = f"Overdue Book Notification: {self.book.title}"
        message = f"Dear {self.user.username},\n\nThe book '{self.book.title}' was due on {self.due_date}. Please return it as soon as possible."
        recipient_list = [self.user.email]
        
        # Call the Celery task to send the email asynchronously
        send_email_async.delay(subject, message, recipient_list)

    def check_overdue(self):
        """
        Check if the transaction is overdue and send notification.
        """
        if self.return_date is None and timezone.now() > self.due_date:
            self.is_returned = True
            self.send_overdue_notification()  # Send email if overdue
        return self.is_returned
    
    def save(self, *args, **kwargs):
        """
        Override the save method to ensure there are available copies of the book before checkout.
        """
        # If this is a new transaction (i.e., book being checked out)
        if not self.is_returned and self.book.available_copies <= 0:
            raise ValidationError("No copies available for this book.")
        
        # Reduce available copies on checkout
        if not self.is_returned:
            self.book.available_copies -= 1
            self.book.save()

        super(Transaction, self).save(*args, **kwargs)
    
    def notify_book_available(self, book):
        """
        Notify the user when a previously unavailable book becomes available via email.
        This method will send the notification asynchronously using Celery.
        """
        subject = f"Book Available: {book.title}"
        message = f"Dear {self.user.username},\n\nThe book '{book.title}' is now available for checkout."
        recipient_list = [self.user.email]
        
        # Call the Celery task to send the email asynchronously
        send_email_async.delay(subject, message, recipient_list)

    def __str__(self):
        return f'{self.book.title} checked out by {self.user.username}'
    
class Overdue(models.Model):
    """
    Model to track overdue books and associated penalties.
    Fields include:
        - transaction: ForeignKey to the Transaction.
        - overdue_date: The date when the book became overdue.
        - penalty_amount: The penalty amount for late returns.
        - is_paid: Boolean indicating if the penalty has been paid.
    """
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    overdue_date = models.DateTimeField(auto_now_add=True)
    penalty_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Overdue record for {self.transaction.book.title} by {self.transaction.user.username}'


class Notification(models.Model):
    """
    Model to manage notifications for users.
    Fields include:
        - user: ForeignKey to the User.
        - book: ForeignKey to the Book.
        - notification_type: Type of notification (e.g., Overdue, Availability).
        - notification_date: Date and time when the notification was sent.
        - is_read: Boolean indicating if the notification has been read.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    notification_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} - {self.notification_type}'