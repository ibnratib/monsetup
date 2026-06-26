from rest_framework import permissions


class IsProductOwner(permissions.BasePermission):
    """
    Permission : seul le vendeur peut modifier/supprimer son annonce.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.seller
