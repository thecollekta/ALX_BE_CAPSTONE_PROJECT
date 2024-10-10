# library_management_system/accounts/permissions.py

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user or request.user.is_staff

class CanManageUsers(permissions.BasePermission):
    """
    Custom permission to only allow admin users to manage user accounts.
    """

    def has_permission(self, request, view):
        # Only admin users can manage user accounts
        return request.user and request.user.is_staff

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
    
class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'member'
    
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

class CanCheckoutBooks(permissions.BasePermission):
    """
    Custom permission to only allow active users to checkout books.
    """

    def has_permission(self, request, view):
        # Only active users can checkout books
        return request.user and request.user.is_active