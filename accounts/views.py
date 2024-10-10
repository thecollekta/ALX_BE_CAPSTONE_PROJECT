# library_management_system/accounts/views.py

from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from transactions.models import Transaction
from rest_framework import filters
from .serializers import (CustomUserSerializer, RegistrationSerializer, 
                          LoginSerializer, LogoutSerializer)
from transactions.serializers import TransactionSerializer
from .permissions import (IsOwnerOrAdmin, CanManageUsers)
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class CustomUserViewSet(viewsets.ModelViewSet):
    """
    A Viewset for viewing and editing user instances.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email']  # Specify fields to ued for ordering
    ordering = ['id']

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def borrowed_books(self, request, pk=None):
        user = self.get_object()
        transactions = Transaction.objects.filter(user=user, is_returned=False)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

@swagger_auto_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling user registration. Create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'password2': openapi.Schema(type=openapi.TYPE_STRING),
                
            }
        ),
        operation_description="Create a new user account",
        responses={
            201: CustomUserSerializer,
            400: "Bad request"
        },
        examples={
            "application/json": {
                "username": "sam",
                "password": "passing123",
                "email": "sam@gmail.com"
            }
        }
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response({
            "user": serializer.data,
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """
        If the user is admin, return all users, else only the authenticated user's information.
        """
        if self.request.user.is_staff:
            return User.objects.all()  # Admin can view all users
        return User.objects.filter(id=self.request.user.id)  # Members can view their own profile

class LoginViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users with role-based access control.
    Admin users can perform all CRUD operations, while regular users can view their own details.
    """
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        """Determine the permission classes based on user role."""
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LogoutViewSet(viewsets.ViewSet):
    """A ViewSet for logging out users"""
    authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)