#coding:utf-8
'''
Created on 2016年9月7日

@author: lch
'''
from django.shortcuts import render
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http.response import Http404, JsonResponse
from captcha.views import imageV, generateCap,imageV_notDelete
from account.models import MyUser
from account.varify import verifymobilecode

def forgot_passwd(request):
    if request.method == "POST":
        if not request.is_ajax():
            raise Http404
        result={}
        passwd = request.POST.get('passwd', '')
        telcode = request.POST.get("code", '')
        mobile = request.POST.get('mobile', '')
        if not (passwd and telcode and mobile):
            result['code'] = '3'
            result['res_msg'] = u'传入参数不足！'
            return JsonResponse(result)
        ret = verifymobilecode(mobile,telcode)
        if ret != 0:
            result['code'] = 1
            if ret == -1:
                result['res_msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['res_msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['res_msg'] = u'手机验证码已过期，请重新获取'
        else:
            user = MyUser.objects.get(mobile=mobile)
            user.set_password(passwd)
            user.save(update_fields=["password"])
            result['code'] = 0
        return JsonResponse(result)
    else:
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)
        return render(request,'registration/forgot_passwd.html',
                  {'hashkey':hashkey, 'codimg_url':codimg_url})
        

def validate_randcode(request):
    result = {'code':-1}
    hashkey = request.GET.get('hashkey', None)
    response = request.GET.get('response', None)
    phone = request.GET.get('mobile', None)
    if not (hashkey and response and phone):
        raise Http404
    ret = imageV_notDelete(hashkey, response)
    if ret != 0:
        result['code'] = 1
        result.update(generateCap())
        return JsonResponse(result)
    try:
        MyUser.objects.get(mobile=str(phone))
    except MyUser.DoesNotExist:
        result['code'] = 2
    else:
        result['code'] = 0
    return JsonResponse(result)

def validate_telcode(request):
    result={}
    mobile = request.GET.get("mobile", '')
    telcode = request.GET.get("code", '')
    ret = verifymobilecode(mobile,telcode)
    if ret != 0:
        result['code'] = 1
        if ret == -1:
            result['res_msg'] = u'请先获取手机验证码'
        elif ret == 1:
            result['res_msg'] = u'手机验证码输入错误！'
        elif ret == 2:
            result['res_msg'] = u'手机验证码已过期，请重新获取'
    else:
        result['code'] = 0
    return JsonResponse(result)