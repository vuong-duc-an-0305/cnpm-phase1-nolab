from typing import Iterable

from rest_framework.permissions import BasePermission


def _user_in_groups(user, group_names: Iterable[str]) -> bool:
    return bool(user and user.is_authenticated and user.groups.filter(name__in=group_names).exists())


class IsAdminRole(BasePermission):
    """Allow access only to users belonging to the admin group or superusers."""

    def has_permission(self, request, view):
        # Superuser luôn có quyền
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        # Hoặc thuộc group admin
        return _user_in_groups(request.user, ['admin'])


class IsAdminOrCashierRole(BasePermission):
    """Allow access to users in admin, manager, cashier or waiter groups, or superusers."""

    def has_permission(self, request, view):
        # Superuser luôn có quyền
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        # Hoặc thuộc group admin/manager/cashier/waiter
        return _user_in_groups(request.user, ['admin', 'manager', 'cashier', 'waiter'])
