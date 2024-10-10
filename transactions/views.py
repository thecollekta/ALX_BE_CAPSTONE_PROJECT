# library_management_system/transactions/views.py

from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Book, Transaction
from .serializers import TransactionSerializer
from accounts.permissions import CanCheckoutBooks
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.tasks import send_email_async
from rest_framework.exceptions import ValidationError

@swagger_auto_schema(tags=['Transactions'])
class TransactionViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing book checkouts, returns and overdue.
    - Check out: Users can check out available books.
    - Return: Users return checked-out books.
    - Overdue: Automatic overdue detection and flagging.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, CanCheckoutBooks]

    @swagger_auto_schema(
        operation_description="Check for overdue books and send notifications.",
        responses={
            200: openapi.Response(
                description="Notifications sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Unauthorized",
            403: "Permission denied"
        }
    )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        POST endpoint to allow users to check out books.
        Reduces available copies and sets a due date.
        """
        book = Book.objects.get(pk=pk)
        if book.available_copies > 0:
            transaction = Transaction.objects.create(
                user=request.user,
                book=book,
                check_out_date=timezone.now(),
                due_date=timezone.now() + timezone.timedelta(days=14)
            )
            book.available_copies -= 1
            book.save()
            return Response({'status': 'book checked out', 'due_date': transaction.due_date})
        return Response({'error': 'No available copies'}, status=400)

    def perform_return(self, transaction):
        """
        Handles the book return process, updating return date and checking overdue status.
        """
        transaction.return_date = timezone.now()
        transaction.is_overdue = transaction.check_overdue()
        transaction.save()

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        List all transactions where the book is overdue.
        """
        overdue_transactions = Transaction.objects.filter(is_overdue=True)
        for transaction in overdue_transactions:
            transaction.send_overdue_notification()
            
        serializer = self.get_serializer(overdue_transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        """
        Custom action to handle book returns.
        It marks the transaction as returned, updates the book's available copies,
        and logs the return date.
        """
        try:
            transaction = self.get_object()  # Get transaction instance by its primary key
            if transaction.is_returned:
                return Response({'detail': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark book as returned and update related fields
            transaction.is_returned = True
            transaction.return_date = timezone.now()
            transaction.book.available_copies += 1  # Increase available copies of the book
            transaction.book.save()
            transaction.save()

            # Notify users waiting for the book if copies are now available
            if transaction.book.available_copies > 0:
                transaction.notify_book_available(transaction.book)
            
                return Response({"status": "Book returned and users notified if applicable."})

            return Response({'detail': 'Book returned successfully!'}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({'detail': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
            """
            Custom behavior on transaction update, i.e, marking a book as returned.
            """
            instance = serializer.save()
            if instance.is_returned:
                subject = 'Book Returned'
                message = f'You have successfully returned the book "{instance.book.title}". Thank you!'
                recipient_list = [instance.user.email]
                send_email_async.delay(subject, message, recipient_list)  # Call Celery task