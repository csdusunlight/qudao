#coding:utf-8
'''
Created on 2017年7月19日

@author: lch
'''
from django.http.response import HttpResponse
def has_permission(code):
    def decorator(view):
        def wrapper(request, *args, **kw):
            user = request.user
            if user.has_admin_perms(code):
                return view(request, *args, **kw)
            else:
                return HttpResponse(status=403)
        return wrapper
    return decorator