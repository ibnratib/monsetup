from rest_framework import permissions


class IsReviewedSeller(permissions.BasePermission):
    """Le vendeur noté peut répondre à l'avis."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.seller
