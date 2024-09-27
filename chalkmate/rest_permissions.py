from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

# from profiles.models import UserProfileMap


class IsAdminOrCreateOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        return request.method.lower() == 'post'


class IsAdminOrIsSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user == obj or request.user.is_staff


class IsSelfOrNotUpdate(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsAdminOrReferredNotSet(permissions.BasePermission):
    message = "cannot set referred_by when it already exists"

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (not bool(obj.referred_by)) or request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):

    message = "you do not own this object"

    def has_object_permission(self, request, view, obj):
        return True if request.method in SAFE_METHODS else \
            (hasattr(obj, 'owner') and obj.owner == request.user) or \
            (hasattr(obj, 'profile') and obj.profile.owner == request.user)


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method.lower() == 'post'


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of profile to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# class IsAdminOrProfileNotSet(permissions.BasePermission):

#     message = "cannot set profile when it already exists"

#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#         elif request.method.lower() == 'post':
#             return (not UserProfileMap.objects.filter(user=request.user).exists()) or request.user.is_staff
#         else:
#             return True

# class DisallowListView(permissions.BasePermission):

#     def has_permission(self, request, view):

#         if (view.action == 'list'):
#             return False
        
#         return True
