from rest_framework import permissions


class IsBookingGuestOrHotelOwnerOrSuperAdmin(permissions.BasePermission):
    """
    Allow access to a booking if the user is the guest (booking owner),
    the hotel owner (host), or a superuser.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        if obj.user_id == request.user.id:
            return True
        return False
