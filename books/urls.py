# library_management_system/books/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register('books', BookViewSet, basename='books')

urlpatterns = [
   path('', include(router.urls)),
]