from rest_framework.permissions import BasePermission
from canteen.models import User
class IsCanteenAdmin(BasePermission):
    """
    Allows access only to users with the CANTEEN_ADMIN role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 2

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    

class IsCanteenAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_superuser or
                request.user.role == User.CANTEEN_ADMIN 
            )
        )