from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)


class AnonymousReadOnlyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user is None or user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
