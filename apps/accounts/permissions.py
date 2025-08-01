from rest_framework import permissions

class IsPatient(permissions.BasePermission):
    """
    Permission class to check if user is a patient.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'

class IsDoctor(permissions.BasePermission):
    """
    Permission class to check if user is a doctor.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'doctor'

class IsSuperuser(permissions.BasePermission):
    """
    Permission class to check if user is a superuser.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser
