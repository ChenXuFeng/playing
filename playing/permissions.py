from rest_framework.permissions import BasePermission


class Permission(BasePermission):
    message='无权限'

    def has_permission(self, request, view):
        return request.user.is_superuser
