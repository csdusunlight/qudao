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
        return request.user.is_staff
    def has_object_permission(self, request, view, obj):
        # 查看的权限对所有请求开放
        # 所以我们永远开放 GET, HEAD or OPTIONS 请求
#         if request.method in permissions.SAFE_METHODS:
#             return True

        # 写的请求只对对象的创建者开放
        return request.user.is_staff
    
from rest_framework.authentication import SessionAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening