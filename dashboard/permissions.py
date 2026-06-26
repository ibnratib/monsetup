from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    """
    Permission : seul le propriétaire de la notification peut la modifier.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
