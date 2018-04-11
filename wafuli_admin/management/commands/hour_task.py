#coding:utf-8
'''
Created on 2016年8月29日

@author: lch
'''
import logging
from django.core.management.base import BaseCommand
from account.models import MyUser
from django.db.models import F
import datetime
import time
from account.varify import httpconn
from wafuli_admin.models import Dict
from django.conf import settings
from weixin.models import WeiXinUser
from weixin.settings import submit_investlog_notify_templateid
from dragon.settings import APPID
from xiaochengxu.models import App
from django.core.cache import cache
from coupon.models import UserCoupon
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Hour-task is beginning*********")
        begin_time = time.time()
        now = datetime.datetime.now()
        start = datetime.datetime(now.year, now.month, now.day, now.hour, 0, 0)
        to = start + datetime.timedelta(hours=1)
        access_token = update_accesstoken()
        update_jsapi_ticket(access_token)
        update_xcxaccesstoken()
#         sendTemplate(access_token)
        check_coupon()
        end_time = time.time()
        logger.info("******Hour-task is finished, time:%s*********",end_time-begin_time)
        
def update_accesstoken():
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type':'client_credential',
        'appid':settings.APPID,
        'secret':settings.SECRET,
    }
    json_ret = httpconn(url, params, 0)
    if 'access_token' in json_ret and 'expires_in' in json_ret:
        access_token = json_ret['access_token']
        now = int(time.time())
        expire_stamp = now + json_ret['expires_in']
        defaults={'value':access_token, 'expire_stamp':expire_stamp}
        Dict.objects.update_or_create(key='access_token', defaults=defaults)
        return access_token
    else:
        logger.error('Getting access_token error:' + str(json_ret) )
        return ''
def update_jsapi_ticket(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
    params = {
        'type':'jsapi',
        'access_token':access_token,
    }
    json_ret = httpconn(url, params, 0)
    if 'ticket' in json_ret and 'expires_in' in json_ret:
        jsapi_ticket = json_ret['ticket']
        now = int(time.time())
        expire_stamp = now + json_ret['expires_in']
        defaults={'value':jsapi_ticket, 'expire_stamp':expire_stamp}
        Dict.objects.update_or_create(key='jsapi_ticket', defaults=defaults)
    else:
        logger.error('Getting access_token error:' + str(json_ret) )

def sendTemplate(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + access_token
    kwarg = {}
    kwarg.update(access_token=access_token, template_id=submit_investlog_notify_templateid)
    to_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + APPID +"&redirect_uri=http%3A%2F%2Ftest.fuliunion.com%2Fweixin%2Fbind-user%2F&response_type=code&scope=snsapi_userinfo"
    kwarg.update(url=to_url, topcolor="#FF0000")
    wusers = WeiXinUser.objects.all()
    for wu in wusers:
        openid = wu.openid
        data = {'first':{'value':u"您的主页有用户成功交单，请及时处理。您的主页有新的预约单，请及时处理。", 'color':"#173177"},
                'keyword1':{'value':u"美易理财三月标", 'color':"#173177"},
                'keyword2':{'value':u"10000元", 'color':"#173177"},
                'keyword3':{'value':u'90天', 'color':"#173177"},
                'remark':{'value':u'如果您不想再收到此类通知，可在个人中心设置里取消微信消息通知', 'color':"#173177"},}
        kwarg.update(data=data, touser=openid)
        ret = httpconn(url, kwarg, 1)
        logger.info(ret)
        
def update_xcxaccesstoken():
    apps = App.objects.filter(state='0')
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    for app in apps:
        app_id = app.app_id
        app_secret = app.app_secret
        params = {
            'grant_type':'client_credential',
            'appid':app_id,
            'secret':app_secret,
        }
        json_ret = httpconn(url, params, 0)
        if 'access_token' in json_ret and 'expires_in' in json_ret:
            access_token = json_ret['access_token']
            now = int(time.time())
            expire_stamp = now + json_ret['expires_in']
            app.access_token = access_token
            app.expire_stamp = expire_stamp
            app.save(update_fields=['access_token', 'expire_stamp'])
        else:
            logger.error('Getting access_token for %s error: %s' % (app_id, str(json_ret)) )

def check_coupon():
    users = ''
    with cache.lock("admin_invest"):
        users = cache.get('invest_user_set')
        cache.set('invest_user_set', '')
    if users:
        users = users.split(',')
        users = [ int(x) for x in users ]
        user_set = set(users)
        print user_set
        coupons = UserCoupon.objects.filter(user_id__in=user_set, state='0',
                                   expire__gt=datetime.date.today())
        for coupon in coupons:
            coupon.checklock()