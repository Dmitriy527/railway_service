from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrIsAuthenticatedReadOnly(BasePermission):
    """
    The request is authenticated as an admin - read/write,
    if a user - read only request
    """

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.method in SAFE_METHODS
        ) or (request.user and request.user.is_staff)
