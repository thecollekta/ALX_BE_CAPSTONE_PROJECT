# library_management_system/books/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Book(models.Model):
    """
    Model representing a book in the library with attributes including title,
    author, published date, and number of available copies.
    """
    title = models.CharField(max_length=200, db_index=True)
    author = models.CharField(max_length=200, db_index=True)
    isbn = models.CharField(max_length=13, unique=True, db_index=True)
    published_date = models.DateField()
    available_copies = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Order books by title by default
        """
        ordering = ['title']

        """
        Ensures the permissions can be added to either the Librarian or Member.
        """
        permissions = [
            ("can_borrow_books", "Can borrow books"),
            ("can_manage_books", "Can manage books"),
        ]

        indexes = [
            models.Index(fields=['published_date']),  # Index for date searches
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    def clean(self):
        """
        Custom validation to ensure ISBN is exactly 13 characters long.
        """
        if len(self.isbn) != 13:
            raise ValidationError({'isbn': 'ISBN must be exactly 13 characters long.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)