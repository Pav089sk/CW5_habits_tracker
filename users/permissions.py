from rest_framework import permissions


class IsFounder(permissions.BasePermission):
    """
       Класс для разрешения создателю объекта.
    """
    def has_object_permission(self, request, view, obj):
        return obj.founder == request.user
