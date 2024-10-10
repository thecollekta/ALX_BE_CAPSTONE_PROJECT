# library_management_system/accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginViewSet, LogoutViewSet, CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('register', UserViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('logout', LogoutViewSet, basename='logout')

urlpatterns = [
   path('', include(router.urls)),
]