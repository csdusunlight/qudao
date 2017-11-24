#coding:utf-8
from django.shortcuts import render, redirect
import hashlib
from django.http.response import HttpResponse,Http404, JsonResponse
import logging
from account.models import MyUser
from .models import WeiXinUser
from django.views.decorators.csrf import csrf_exempt
from wafuli_admin.models import Dict
logger = logging.getLogger('wafuli')
from account.varify import httpconn, verifymobilecode
from django.conf import settings
from django.contrib.auth import login as auth_login

@csrf_exempt
def weixin(request):
    token = '1hblsqTsdfsdfsd'
    timestamp = str(request.GET.get('timestamp'))
    nonce = str(request.GET.get('nonce'))
    signature = str(request.GET.get('signature'))
    echostr = str(request.GET.get('echostr'))
    paralist = [token,timestamp,nonce]
    paralist.sort()
    parastr = ''.join(paralist)
    siggen = hashlib.sha1(parastr).hexdigest()
    if siggen==signature:
        return HttpResponse(echostr)
    else:
        raise Http404

def bind_user(request):
    if request.method == 'POST':
        result = {}
        openid = request.session['openid']
        access_token = request.session['access_token']
        if not openid or not access_token:
            result['code'] = '3'
            result['msg'] = u'请在微信中提交'
            return JsonResponse(result)
        mobile = request.POST.get('mobile')
        telcode = request.POST.get('telcode')
        ret = verifymobilecode(mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['msg'] = u'手机验证码已过期，请重新获取'
        else:
            result['code'] = 0
            weixinuser = WeiXinUser.objects.filter(openid=openid).first()
            if not weixinuser:
                params = {
                    'access_token':access_token,
                    'openid':openid,
                    'lang':'zh_CN',
                    'code':'',
                }
                url = 'https://api.weixin.qq.com/sns/userinfo'
                json_ret = httpconn(url, params, 0)
                weixinuser = WeiXinUser.objects.create(openid=json_ret.get('openid', ''), nickname=json_ret.get('nickname', ''), 
                                    sex=json_ret.get('sex',''), province=json_ret.get('province', ''), 
                                    city=json_ret.get('city',''), country=json_ret.get('country', ''), 
                                    headimgurl=json_ret.get('headimgurl',''), unionid=json_ret.get('unionid', ''),)
            try:
                user = MyUser.objects.get(mobile=mobile)
            except MyUser.DoesNotExist:
                request.session['mobile'] = mobile
                result['msg'] = u'您尚未注册，请先通过浏览器注册'
                result['url'] = "/weixin/bind-user/nouser/"
            else:
                user.backend = 'django.contrib.auth.backends.ModelBackend'#为了略过用户名和密码验证
                auth_login(request, user)
                result['url'] = "/account/"
                if not weixinuser.user:
                    weixinuser.user = user
                    weixinuser.save(update_fields=['user'])
        return JsonResponse(result)    
    else:
        code = request.GET.get('code','')
        if not code:
            return HttpResponse(u"微信授权失败，请稍后再试")
        url = ' https://api.weixin.qq.com/sns/oauth2/access_token'
        logger.info(code)
        params = {
            'grant_type':'authorization_code',
            'appid':settings.APPID,
            'secret':settings.SECRET,
            'code':code,
        }
        json_ret = httpconn(url, params, 0)
        if 'openid' in json_ret:
            openid = json_ret['openid']
            access_token = json_ret['access_token']
            request.session['openid'] = openid
            request.session['access_token'] = access_token
            try:
                user = WeiXinUser.objects.get(openid=openid).user
            except WeiXinUser.DoesNotExist:
                return render(request, 'm_bind.html')
            else:
                if not user:
                    return render(request, 'm_bind.html')
                user.backend = 'django.contrib.auth.backends.ModelBackend'#为了略过用户名和密码验证
                auth_login(request, user)
                return redirect('account_index')
        else:
            logger.error('Getting access_token error:' + str(json_ret) )
            return HttpResponse(u"本页面转发或刷新无效，请在微信公众号中重新打开")

def bind_user_success(request):
    return render(request, 'm_bind_success.html')
def bind_user_setpasswd(request):
    return render(request, 'm_bind_setpasswd.html')

def sendWeixinTemplate():
    access_token = Dict.objects.get(key='access_token')
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + access_token
    kwarg = {}
    kwarg.update(access_token=access_token, template_id='XKGoq0xWvXrg5alO_3pc4f4F5wKR7EDnfvzPoUlh-wY')
    to_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx76aa03447c27f99d&redirect_uri=http%3A%2F%2Ftest.wafuli.cn%2Fweixin%2Fbind-user%2F&response_type=code&scope=snsapi_userinfo"
    kwarg.update(url=to_url, topcolor="#FF0000")
    wusers = WeiXinUser.objects.all()
    for wu in wusers:
        openid = wu.openid
        data = {'user':{'value':wu.user.username, 'color':"#173177"},}
        kwarg.update(data=data, touser=openid)
        ret = httpconn(url, kwarg, 1)
        logger.info(ret)
    