#coding:utf-8
'''
Created on 2017年7月3日

@author: lch
'''
from rest_framework import permissions
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True

        # 写的请求只对对象的创建者开放
        if not request.user.is_authenticated():
            return False
        return request.user.is_staff

    
from rest_framework.authentication import SessionAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
    
class IsOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated():
            return False
        return request.user.is_staff or obj.user == request.user 
