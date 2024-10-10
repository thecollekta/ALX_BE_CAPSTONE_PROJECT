# library_management_system/accounts/tests.py

from django.test import TestCase
# from .models import CustomUser
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# Test for CustomUser Model
class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.role, User.MEMBER)

# Test for Views
class UserViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', 
            password='adminpass', 
            email='admin@example.com'
        )
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123', 
            email='test@example.com'
        )
        self.client.login(username='admin', password='adminpass')