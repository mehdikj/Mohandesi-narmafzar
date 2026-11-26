from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Resource
class ResourceAccessPermission(BasePermission):
    def has_permission(self,request,view):
        if request.method in SAFE_METHODS: return True
        return bool(request.user.is_authenticated and request.user.is_librarian())
    def has_object_permission(self,request,view,obj):
        if request.method not in SAFE_METHODS: return bool(request.user.is_authenticated and request.user.is_librarian())
        if obj.status!=Resource.Status.PUBLISHED: return bool(request.user.is_authenticated and request.user.is_librarian())
        if obj.access_policy==Resource.AccessPolicy.PUBLIC: return True
        return bool(request.user.is_authenticated and obj.access_policy==Resource.AccessPolicy.REGISTERED_ONLY)
