from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == ['GET', 'HEAD', 'OPTION']:
                return True

        return request.user == obj.created_by



class IsProductOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
