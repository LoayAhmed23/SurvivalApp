from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadAuthenticatedOrEditOwn(BasePermission):
    """
    Allows only authenticated users to view and create objects,
    and only the owner of an object to update or delete it.
    """
    def has_permission(self, request, view):
        """Only Authenticated Users"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        """Only object owner"""
        return obj.user == request.user
