from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Предоставляет доступ на изменение данных только автору."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )
