from rest_framework.permissions import BasePermission

class IsCanteenAdmin(BasePermission):
    """
    Allows access only to users with the CANTEEN_ADMIN role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 2
