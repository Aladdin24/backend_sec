# documents/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Autorise uniquement les utilisateurs avec is_staff=True.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff