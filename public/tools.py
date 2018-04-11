#coding:utf-8
'''
Created on 2017年9月11日

@author: lch
'''
from django.http.response import HttpResponse
from account.varify import send_multimsg_bydhst
def has_post_permission(code):
    def decorator(view):
        def wrapper(request, *args, **kw):
            user = request.user
            if user.is_authenticated() and (request.method != 'POST' or user.has_admin_perms(code)):
                return view(request, *args, **kw)
            else:
                return HttpResponse(status=403)
        return wrapper
    return decorator

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
    
def str_to_bool(chars):
    if type(chars)==bool:
        return chars
    to_dic = {
        'false': False,
        'False': False,
        'True': True,
        'true': True,
    }
    return to_dic[chars]

def send_mobilemsg_multi(phone_list, content):
    if not content or len(content)==0 or len(phone_list)==0:
        return 0
    phone_list = list(set(phone_list))
    length = len(phone_list)
    times = length/500
    tnum = 0
    if length%500 > 0:
        times += 1
    for t in range(times):
        frag_list = phone_list[t*500:t*500+500]
        phones = ','.join(frag_list)
        reg = send_multimsg_bydhst(phones, content)
        if reg==0:
            tnum += len(frag_list)
    return tnum
    