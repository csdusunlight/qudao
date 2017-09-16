#coding:utf-8
'''
Created on 2017年9月11日

@author: lch
'''
from django.http.response import HttpResponse
def has_permission(code):
    def decorator(view):
        def wrapper(request, *args, **kw):
            user = request.user
            if user.is_authenticated() and user.is_staff and (request.method != 'POST' or user.has_admin_perms(code)):
                return view(request, *args, **kw)
            else:
                return HttpResponse(status=403)
        return wrapper
    return decorator

def login_required_ajax(function=None,redirect_field_name=None): 
    """
    Just make sure the user is authenticated to access a certain ajax view Otherwise return a HttpResponse 401 
    - authentication required instead of the 302 redirect of the original Django decorator 
    """ 
    def _decorator(view_func): 
        def _wrapped_view(request, *args, **kwargs): 
            if request.user.is_authenticated(): 
                return view_func(request, *args, **kwargs) 
            else: 
                return HttpResponse(status=401) 
        return _wrapped_view 
    
    if function is None: 
        return _decorator 
    else: 
        return _decorator(function)