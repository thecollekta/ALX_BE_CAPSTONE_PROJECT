# library_management_system/accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_of_membership', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        """
        user = User.objects.create_user(**validated_data)
        return user
    
class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    This serializer handles user data input validation and password hashing.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # Confirm password field

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        """
        Ensure that the two password fields match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields do not match."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with the validated data and hashed password.
        """
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  # Hashes password
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for logging in users. 
    It authenticates users based on their username and password and returns JWT tokens.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """
        Validate user credentials and return the user object if authentication is successful.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        # If the user is authenticated, generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return {
            'user': {
                'username': user.username,
                'email': user.email
            },
            'tokens': tokens
        }

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for handling the user logout request.
    It ensures that the refresh_token is provided and valid.
    """
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        """
        Validate the refresh token.
        """
        try:
            RefreshToken(value)
        except Exception as _:
            raise serializers.ValidationError("Invalid token or token already blacklisted.")
        return value