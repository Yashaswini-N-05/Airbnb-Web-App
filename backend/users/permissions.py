from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsSuperAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow super admins to edit/delete.
    """
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for super admins
        return request.user and request.user.is_superuser


class IsHostOrReadOnly(BasePermission):
    """
    Permission that allows hosts to create/edit their own properties,
    and read access to all authenticated users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for hosts and super admins
        return request.user.is_host() or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For hotels, check if user is the owner or super admin
        if hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_superuser
        
        # For rooms, check through hotel ownership
        if hasattr(obj, 'hotel') and hasattr(obj.hotel, 'owner'):
            return obj.hotel.owner == request.user or request.user.is_superuser
            
        return request.user.is_superuser


class IsGuestOrHost(BasePermission):
    """
    Permission for guests and hosts (booking related operations).
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_guest() or request.user.is_host() or request.user.is_superuser))


class IsVerifiedHost(BasePermission):
    """
    Permission that requires user to be a verified host.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.is_host() and request.user.is_verified_host)


class IsSuperAdmin(BasePermission):
    """
    Permission that only allows super admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_superuser


class IsOwner(BasePermission):
    """
    Permission that only allows owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if object has owner attribute
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Check if object is the user itself
        elif hasattr(obj, 'email') and hasattr(request.user, 'email'):
            return obj == request.user
        return False


class IsOwnerOrSuperAdmin(BasePermission):
    """
    Permission that allows owners and super admins.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if object has owner attribute
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Check if object is the user itself
        elif hasattr(obj, 'email') and hasattr(request.user, 'email'):
            return obj == request.user
        return False


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a profile to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the profile.
        return obj.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow owners or admins to access the object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow access if user is admin
        if request.user.is_staff or request.user.is_admin_user():
            return True
        
        # Allow access if user is the owner
        return obj == request.user


class IsEmailVerified(permissions.BasePermission):
    """
    Custom permission to check if user's email is verified.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.email_verified


class IsAccountActive(permissions.BasePermission):
    """
    Custom permission to check if user's account is active.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_active


# Role-based permissions
class IsGuest(permissions.BasePermission):
    """
    Permission to check if user is a guest (traveler/booker).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_guest()


class IsHost(permissions.BasePermission):
    """
    Permission to check if user is a host (property owner/manager).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_host()


class IsApprovedHost(permissions.BasePermission):
    """
    Permission to check if user is an approved host.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.can_list_properties()


class IsHostOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a host or admin (staff/superuser).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_host() or request.user.is_admin_user()


class IsGuestOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a guest or admin (staff/superuser).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_guest() or request.user.is_admin_user()


class IsHostVerificationOwner(permissions.BasePermission):
    """
    Permission to check if user owns the host verification record.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow read access for admins
        if request.method in permissions.SAFE_METHODS and request.user.is_admin_user():
            return True
        
        # Allow owner access
        return obj.user == request.user 