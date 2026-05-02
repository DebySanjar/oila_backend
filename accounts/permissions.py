"""
Custom permissions for accounts app
"""
from rest_framework import permissions


class IsParent(permissions.BasePermission):
    """
    Permission to only allow parents to access
    """
    message = "Faqat ota-onalar uchun ruxsat berilgan"
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'parent'


class IsChild(permissions.BasePermission):
    """
    Permission to only allow children to access
    """
    message = "Faqat farzandlar uchun ruxsat berilgan"
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'child'


class IsSameFamily(permissions.BasePermission):
    """
    Permission to only allow access to same family members
    """
    message = "Faqat bir oila a'zolari uchun ruxsat berilgan"
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has family_code attribute
        if hasattr(obj, 'family_code'):
            return obj.family_code == request.user.family_code
        
        # Check if the object is a User
        if hasattr(obj, 'user_type'):
            return obj.family_code == request.user.family_code
        
        return False


class IsOwnerOrParent(permissions.BasePermission):
    """
    Permission to allow owner or parent to access
    """
    message = "Faqat egasi yoki ota-ona uchun ruxsat berilgan"
    
    def has_object_permission(self, request, view, obj):
        # Owner can access
        if obj == request.user:
            return True
        
        # Parent can access child's data
        if request.user.user_type == 'parent':
            if hasattr(obj, 'family_code'):
                return obj.family_code == request.user.family_code
        
        return False
