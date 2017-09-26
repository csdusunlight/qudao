#coding:utf-8
import urllib, urllib2, json
from .models import MobileCode
import time as ttime
from datetime import datetime
import hmac
import base64
from hashlib import sha1, md5
import logging
from account.tools import random_str, random_code
from wafuli_admin.models import Message_Record
logger = logging.getLogger("wafuli")
# typ: 0:get  1:post
def httpconn(url, para, typ):
    if typ == 0:
        data = urllib.urlencode(para)
        url = url + '?' + data
        req = urllib2.Request(url)
    else:
        data = json.dumps(para)
        req = urllib2.Request(url,data)
    try:
        con = urllib2.urlopen(req,timeout=10)
    except Exception as e:
        logger.error(e)
        return None
        #something you should do
    ret = json.load(con)
    return ret
def verifymobilecode(phone, code):
    mobileCode = MobileCode.objects.filter(mobile=phone).first()
    if mobileCode is None:
        logger.info('No mobile varifing code is found in database!')
        return -1
    if code != mobileCode.rand_code:
        logger.info('The mobile varifing code is not correct!')
        return 1
    elif  (datetime.now() - mobileCode.create_at).seconds > 10*60:
        logger.info('The mobile varifing code has already expired!')
        return 2
    else:
        return 0



def get_access_token(app_id, app_secret, obj):
    url_at = 'https://oauth.api.189.cn/emp/oauth2/v3/access_token'
    param = {'grant_type':'client_credentials',
             'app_id':app_id,
             'app_secret':app_secret,
    }
    json_ret = httpconn(url_at, param, 1)
    logger.info('json returned from 189:' + str(json_ret))
    if not json_ret:
        return None, None
    try:
        return json_ret['access_token'],json_ret['expires_in']
    except:
        return None, None

#该方法测试不通，可能为电信服务器问题
# def refresh_access_token(app_id, app_secret):
#     url_at = 'https://oauth.api.189.cn/emp/oauth2/v3/access_token'
#     param = {'grant_type':'refresh_token',
#              'refresh_token':'10af96c85a79dace66c8a8a82a6bcda21458046932039',
#              'app_id':app_id,
#              'app_secret':app_secret,
#     }
#     json_ret = httpconn(url_at, param, 1)
#     print 'ddddd',json_ret
#     if not json_ret:
#         return None
#     try:
#         return json_ret['access_token'],json_ret['expire']
#     except:
#         return None
def get_token(app_id, app_secret, access_token, timestamp):
    logger.info('***********getting token from 189*************')
    param = {
                     'app_id':app_id,
                     'access_token':access_token,
                     'timestamp':timestamp
    }
    items = param.items()
    items.sort()
    l = []
    for k, v in items:
        l.append(k + '=' + v)
    para_str = '&'.join(l)
    sign = hmac.new(str(app_secret),str(para_str), sha1).digest()
    sign = base64.b64encode(sign)
    param['sign'] = sign
    url_token = 'http://api.189.cn/v2/dm/randcode/token'
    json_ret = httpconn(url_token, param, 0)
    logger.info('json returned from 189:' + str(json_ret))
    if json_ret and 'res_message' in json_ret.keys():
        if 'expired' in json_ret['res_message']:
            return ''
        else:
            return None
    try:
        return json_ret['token']
    except:
        return None
def sendmsg_by189(app_id, app_secret, access_token, token, timestamp, phone):
    param = {
                     'app_id':app_id,
                     'access_token':access_token,
                     'token':token,
                     'phone':phone,
                     'url':'http://www.wafuli.cn/account/callback/',
                     'exp_time':'10',
                     'timestamp':timestamp,
    }
    items = param.items()
    items.sort()
    l = []
    for k, v in items:
        l.append(k + '=' + v)
    para_str = '&'.join(l)
    sign = hmac.new(str(app_secret),str(para_str), sha1).digest()
    sign = base64.b64encode(sign)
    param['sign'] = sign
    url_msg = 'http://api.189.cn/v2/dm/randcode/send'
    json_ret = httpconn(url_msg, param, 1)
    logger.info('json returned from 189:' + str(json_ret))
    try:
        if json_ret['res_code'] == 0:
            identifier = json_ret['identifier']
            obj = MobileCode.objects.get(identifier=identifier)
            obj.mobile = phone
            obj.save()
            return 0
        else:
            return -1
    except MobileCode.DoesNotExist:
        logger.info('No MobileCode with this idendifier is found in database!')
        return -1
    except:
        return -1




def sendmsg_bydhst(phone):
    raw_pass = '4i38lwX8'
    m2 = md5()   
    m2.update(raw_pass)   
    code = random_code(6)
    logger.info('Now is sending code to: ' + str(phone))
    content = '尊敬的用户，您的验证码为：' + code + '，本验证码十分钟内有效，感谢您的使用。'
    param = {
                     'account':'dh31921',
                     'password':m2.hexdigest(),
                     'msgid':'2c92825934837c4d0134837dcba00150',
                     'phones':phone,
                     'content':content,
                     'sign':'【挖福利】',
                     'subcode':'',
                     'sendtime':'',
    }
    url_msg = 'http://wt.3tong.net/json/sms/Submit'
    json_ret = httpconn(url_msg, param, 1)
    logger.info('json returned from dhst:' + str(json_ret))
    if json_ret:
        result = json_ret.get('result','-1')
        if result == '0':
            return code
    return None
#群发短信
def send_multimsg_bydhst(phones, content):
    raw_pass = '4i38lwX8'
    m2 = md5()   
    m2.update(raw_pass)
    msgid = random_str(32)
    logger.info('Now is sending code to: ' + str(phones))
    
    param = {
         'account':'dh31921',
         'password':m2.hexdigest(),
         'msgid':msgid,
         'phones':phones,
         'content':content,
         'sign':'【挖福利】',
         'subcode':'',
         'sendtime':'',
    }
    url_msg = 'http://wt.3tong.net/json/sms/Submit'
    json_ret = httpconn(url_msg, param, 1)
    logger.info('json returned from dhst:' + str(json_ret))
    if json_ret:
        retcode = int(json_ret.get('result',-1))
        if retcode == 0:
            Message_Record.objects.create(msgid=msgid, content=content)
        return retcode
    else:
        return -1
#     print('json returned from 189:' + str(json_ret))
def get_report_form_dhst():
    raw_pass = '4i38lwX8'
    m2 = md5()   
    m2.update(raw_pass)   
    param = {
         'account':'dh31921',
         'password':m2.hexdigest(),
         'msgid':'',
         'phones':'',
    }
    url_msg = 'http://wt.3tong.net/json/sms/Report'
    json_ret = httpconn(url_msg, param, 1)
    logger.info('json returned from dhst:' + str(json_ret))
    if json_ret:
        result = json_ret.get('result','-1')
        if result == '0':
            return 0
    return -1