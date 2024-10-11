# library_management_system/books/views.py

from django.shortcuts import render
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination
from books.models import Book
from transactions.models import Transaction
from .serializers import (BookSerializer, TransactionSerializer, BookDetailSerializer)
from accounts.permissions import IsAdminOrReadOnly, CanCheckoutBooks
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@swagger_auto_schema(tags=['Books'])
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book operations in the library system.
    
    This ViewSet provides CRUD operations for books and additional actions
    for checking out and returning books.
    
    Attributes:
        queryset: QuerySet of all books
        serializer_class: Serializer class for book data
        permission_classes: List of permission classes
        authentication_classes: Permission class for JWT Token.
        filter_backends: List of filter backend classes
        filterset_fields: Fields available for filtering
        search_fields: Fields available for searching
        ordering_fields: Fields available for ordering
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'isbn', 'published_date']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author', 'published_date']
    ordering = ['title']

    @swagger_auto_schema(
        operation_description="List all books in the library.",
        manual_parameters=[
            openapi.Parameter(
                'search', 
                openapi.IN_QUERY,
                description="Search by title, author, or ISBN",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', 
                openapi.IN_QUERY,
                description="Order by field (prefix with '-' for descending)",
                type=openapi.TYPE_STRING,
                enum=['title', '-title', 'author', '-author', 'published_date', '-published_date']
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved books list",
                schema=BookSerializer(many=True)
            ),
            401: "Unauthorized"
        }
    )

    def get_queryset(self):
        return Book.objects.all().order_by('title')

    @method_decorator(cache_page(60*15), name='dispatch') # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """
        List all books with optional filtering and caching.
        
        Returns:
            Response: List of all cached books available.
        """
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Checkout a book from the library.",
        responses={
            201: openapi.Response(
                description="Book successfully checked out",
                schema=TransactionSerializer
            ),
            400: "Bad request (no copies available or already checked out)",
            401: "Unauthorized",
            404: "Book not found"
        }
    )

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Returns:
            Serializer class: BookDetailSerializer for retrieve action, 
            BookSerializer otherwise
        """
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer
    

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanCheckoutBooks])
    @transaction.atomic
    def checkout(self, request, pk=None):
        """
        Checkout a book if available.
        
        Args:
            request: HTTP request object
            pk: Primary key of the book
            
        Returns:
            Response: Transaction details or error message
        """
        book = self.get_object()
        user = request.user

        if book.available_copies <= 0:
            return Response(
                {"error": "No copies available for checkout."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Transaction.objects.filter(user=user, book=book, is_returned=False).exists():
            return Response(
                {"error": "You have already checked out this book."},
                status=status.HTTP_400_BAD_REQUEST
            )

        due_date = timezone.now() + timedelta(days=14)
        transaction = Transaction.objects.create(user=user, book=book, due_date=due_date)

        book.available_copies -= 1
        book.save()

        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanCheckoutBooks])
    def return_book(self, request, pk=None):
        """
        Return a checked-out book.
        """
        book = self.get_object()
        user = request.user

        transaction = Transaction.objects.filter(user=user, book=book, is_returned=False).first()
        if not transaction:
            return Response(
                {"error": "You have not checked out this book."},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.is_returned = True
        transaction.return_date = timezone.now()
        transaction.save()

        book.available_copies += 1
        book.save()

        return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        List all the books with available copies.
        """
        books = Book.objects.filter(available_copies__gt=0)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
