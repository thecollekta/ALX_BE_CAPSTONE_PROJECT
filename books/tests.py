# library_management_system/books/tests.py

from django.test import TestCase
from django.utils import timezone
from .models import Book
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.test import RequestFactory
from .serializers import BookSerializer
from accounts.permissions import permissions, IsAdminOrReadOnly

# Test for Book Model
class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date=timezone.now().date(),
            available_copies=5
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.available_copies, 5)

    def test_isbn_validation(self):
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Invalid ISBN Book",
                author="Test Author",
                isbn="123",  # Invalid ISBN
                published_date=timezone.now().date()
            )

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only permissions are allowed for any request.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

# Test for BookView
class BookViewSetTest(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin', password='adminpass', email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date="2023-01-01",
            available_copies=5
        )

    def test_list_books(self):
        url = reverse('books-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book(self):
        url = reverse('books-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '0987654321123',
            'published_date': '2023-05-01',
            'available_copies': 3
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

class BookViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', 
            password='admin123',
            email='admin@example.com'
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date=timezone.now().date(),
            available_copies=5
        )
        self.url = reverse('books-list')

    def test_get_books_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('books-list'))
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_books_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_book(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('books-checkout', kwargs={'pk': self.book.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 3)

# Test for Serializers
class BookSerializerTest(TestCase):
    def setUp(self):
        self.book_attributes = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'published_date': '2023-01-01',
            'available_copies': 5
        }
        self.book = Book.objects.create(**self.book_attributes)
        self.serializer = BookSerializer(instance=self.book)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'title', 'author', 'isbn', 'published_date', 'available_copies']))

    def test_book_serializer_validation(self):
        invalid_data = {
            'title': '',  # Empty title
            'author': 'Test Author',
            'isbn': '123',  # Invalid ISBN
            'published_date': '2023-01-01',
            'available_copies': -1  # Invalid number
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['title', 'isbn', 'available_copies']))

# Test for Permissions
class PermissionTest(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', 
            password='admin123'
        )

    def test_is_admin_or_readonly_permission(self):
        permission = IsAdminOrReadOnly()
        
        # Test GET request (read-only)
        request = self.factory.get('/api/books/')
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test POST request (write)
        request = self.factory.post('/api/books/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test POST request as admin
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))