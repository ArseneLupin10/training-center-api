"""
my custom permissions
"""


from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """permission for authenticated student"""
    def has_permission(self, request, view):
        return not (request.user.is_staff or request.user.is_superuser)

class IsSuperUser(permissions.BasePermission):
    """permission for SuperUser"""
    def has_permission(self, request, view):
        return  request.user.is_superuser

class IsStaff(permissions.BasePermission):
    """permission for Staff User"""
    def has_permission(self, request, view):
        return request.user.is_staff