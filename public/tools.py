#coding:utf-8
'''
Created on 2017年9月11日

@author: lch
'''
import itertools

from django.http import HttpResponse

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
            if user.is_authenticated() and user.has_admin_perms(code):
                return view(request, *args, **kw)
            else:
                return HttpResponse(status=403)
        return wrapper
    return decorator
def is_merchant(view):
    def wrapper(request, *args, **kw):
        user = request.user
        if user.is_merchant == '1':
            return view(request, *args, **kw)
        else:
            return HttpResponse(status=403)
    return wrapper
def is_staff(view):
    def wrapper(request, *args, **kw):
        user = request.user
        if user.is_staff:
            return view(request, *args, **kw)
        else:
            return HttpResponse(status=403)
    return wrapper
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
    phone_list = iter(set(phone_list))
    item = list(itertools.islice(phone_list, 500))
    tnum = 0
    while item:
        phones = ','.join(item)
        print(phones)
        reg = send_multimsg_bydhst(phones, content)
        if reg==0:
            tnum += len(item)
        item = list(itertools.islice(phone_list, 500))
    return tnum
if __name__ == '__main__':
    phone_list = map(str,itertools.islice(itertools.count(1, 1), 1001))
    print(phone_list)
    send_mobilemsg_multi(phone_list,content='nihao')

from random import Random
def random_str(randomlength=5):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str
def random_code(randomlength=6):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str    