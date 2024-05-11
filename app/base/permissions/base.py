from typing import final

from rest_framework.permissions import BasePermission as _BasePermission


class BasePermission(_BasePermission):
    _allow_super: bool = True
    message: str

    def check(self, *args, **kwargs) -> bool:
        return True

    @final
    def has_permission(self, request, view):
        if self._has_permission(request, view):
            return True
        if self._allow_super and getattr(request.user, 'is_superuser', False):
            return True
        return False

    def _has_permission(self, request, view):
        return self.check()

    @final
    def has_object_permission(self, request, view, obj):
        if self._has_object_permission(request, view, obj):
            return True
        if self._allow_super and getattr(request.user, 'is_superuser', False):
            return True
        return False

    def _has_object_permission(self, request, view, obj):
        return self.check()
