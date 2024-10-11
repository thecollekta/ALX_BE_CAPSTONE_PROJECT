# library_management_system/books/serializers.py

from rest_framework import serializers
from .models import Book
from transactions.serializers import TransactionSerializer

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model. 
    It converts the Book model instance to JSON and vice versa.
    """
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'available_copies']

        swagger_schema_fields = {
            "title": "Book",
            "description": "A book in the library system",
            "required": ["title", "author", "isbn", "published_date"],
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "readOnly": True,
                    "description": "Unique identifier for the book"
                },
                "title": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "The title of the book"
                },
                "author": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "The author of the book"
                },
                "isbn": {
                    "type": "string",
                    "maxLength": 13,
                    "minLength": 13,
                    "description": "The ISBN of the book (must be exactly 13 characters)"
                },
                "published_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The publication date of the book"
                },
                "available_copies": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "The number of copies available for checkout"
                }
            }
        }

    def validate_isbn(self, value):
        """
        Check that the ISBN is exactly 13 characters long.
        """
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be exactly 13 characters long.")
        return value

class BookDetailSerializer(BookSerializer):
    """
    Serializer for detailed Book information, including current transactions.
    """
    current_transactions = TransactionSerializer(many=True, read_only=True)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['current_transactions']