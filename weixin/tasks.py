#coding:utf-8
'''
Created on 2017年11月24日

@author: lch
'''
import datetime

import itertools

from wafuli_admin.models import Dict, Message_Log
from weixin.settings import submit_investlog_notify_templateid,\
    book_invest_notify_templateid, withdraw_success_notify_templateid,\
    withdraw_apply_notify_templateid, withdraw_fail_notify_templateid,\
    common_remark
from dragon.settings import APPID, FULIUNION_DOMAIN
from weixin.models import WeiXinUser
from account.varify import httpconn, sendmsg_bydhst, send_multimsg_bydhst
import logging
logger = logging.getLogger('wafuli')


from celery import shared_task  

@shared_task
def sendWeixinNotify(user_obj_list, type):
    access_token = Dict.objects.get(key='access_token').value
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + access_token
    kwarg = {}
    to_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" + APPID +"&redirect_uri=http%3A%2F%2F" + \
        FULIUNION_DOMAIN + "%2Fweixin%2Fbind-user%2F&response_type=code&scope=snsapi_userinfo"
    kwarg.update(url=to_url, topcolor="#FF0000")
    kwarg.update(access_token=access_token)
    if type == 'submit':
        kwarg.update(template_id=submit_investlog_notify_templateid)
        for user_investlog in user_obj_list:
            user = user_investlog[0]
            investlog = user_investlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            project = investlog.project.title
            amount = investlog.invest_amount + u"元"
            term = investlog.invest_term + u"天"
            openid = wuser.openid
            data = {'first':{'value':u"您的主页有用户成功交单，请及时处理。", 'color':"#173177"},
                    'keyword1':{'value':project, 'color':"#173177"},
                    'keyword2':{'value':amount, 'color':"#173177"},
                    'keyword3':{'value':term, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'book':
        kwarg.update(template_id=book_invest_notify_templateid)
        for user_investlog in user_obj_list:
            user = user_investlog[0]
            booklog = user_investlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            project = booklog.project.title
            book_date = booklog.book_date
            qq_number = booklog.qq_number
            openid = wuser.openid
            data = {'first':{'value':u"您的主页有新的预约单，请及时处理。", 'color':"#173177"},
                    'keyword1':{'value':project, 'color':"#173177"},
                    'keyword2':{'value':str(book_date), 'color':"#173177"},
                    'keyword3':{'value':qq_number, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'withdraw_apply':
        kwarg.update(template_id=withdraw_apply_notify_templateid)
        for user_withdrawlog in user_obj_list:
            user = user_withdrawlog[0]
            withdrawlog = user_withdrawlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            amount = str(withdrawlog.amount) + u'元'
            balance = str(user.balance) + u'元'
            withtime = withdrawlog.submit_time.strftime('%Y-%m-%d %H:%M')
            openid = wuser.openid
            data = {'first':{'value':u"福利联盟账户余额（自动）提现通知", 'color':"#173177"},
                    'keyword1':{'value':amount, 'color':"#173177"},
                    'keyword2':{'value':balance, 'color':"#173177"},
                    'keyword3':{'value':withtime, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'withdraw_success_yhk':
        kwarg.update(template_id=withdraw_success_notify_templateid)
        for user_withdrawlog in user_obj_list:
            user = user_withdrawlog[0]
            withdrawlog = user_withdrawlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            amount = str(withdrawlog.amount) + u'元'
            balance = str(user.balance)
            audittime = withdrawlog.audit_time.strftime('%Y-%m-%d %H:%M')
            bank = user.user_bankcard.first()
            openid = wuser.openid
            data = {'first':{'value':u"提现成功，请查收", 'color':"#173177"},
                    'keyword1':{'value':bank.get_bank_display(), 'color':"#173177"},
                    'keyword2':{'value':bank.card_number, 'color':"#173177"},
                    'keyword3':{'value':bank.real_name, 'color':"#173177"},
                    'keyword4':{'value':amount, 'color':"#173177"},
                    'keyword5':{'value':audittime, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'withdraw_success_zhifubao':
        kwarg.update(template_id=withdraw_success_notify_templateid)
        for user_withdrawlog in user_obj_list:
            user = user_withdrawlog[0]
            withdrawlog = user_withdrawlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            amount = str(withdrawlog.amount) + u'元'
            balance = str(user.balance)
            audittime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            zhifubao = user.zhifubao
            zhifubao_real_name = user.zhifubao_real_name
            openid = wuser.openid
            data = {'first':{'value':u"提现成功，请查收", 'color':"#173177"},
                    'keyword1':{'value':u"支付宝", 'color':"#173177"},
                    'keyword2':{'value':zhifubao, 'color':"#173177"},
                    'keyword3':{'value':zhifubao_real_name, 'color':"#173177"},
                    'keyword4':{'value':amount, 'color':"#173177"},
                    'keyword5':{'value':audittime, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'withdraw_fail':
        kwarg.update(template_id=withdraw_fail_notify_templateid)
        for user_withdrawlog in user_obj_list:
            user = user_withdrawlog[0]
            withdrawlog = user_withdrawlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            amount = str(withdrawlog.amount) + u'元'
            audittime = withdrawlog.submit_time.strftime('%Y-%m-%d %H:%M')
            reason = withdrawlog.audit_reason
            openid = wuser.openid
            data = {'first':{'value':u"抱歉，提现审核失败。", 'color':"#FF0900"},
                    'keyword1':{'value':amount, 'color':"#173177"},
                    'keyword2':{'value':audittime, 'color':"#173177"},
                    'keyword3':{'value':reason, 'color':"#173177"},
                    'remark':{'value':common_remark, 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)

@shared_task
def send_msgs_erlei(rtable):
    for item in rtable:
        mobile = item[0]
        content = item[1]
        mobile = str(int(float(mobile)))
        sendmsg_bydhst(mobile, content, sign='【来财商贸】')
        log = Message_Log.objects.create(mobile=mobile, content=content)

@shared_task
def send_msgs_erlei_multi(phone_list, content):
    if not content or len(content)==0 or len(phone_list)==0:
        return 0
    phone_list = iter(set(phone_list))
    item = list(itertools.islice(phone_list, 500))
    tnum = 0
    while item:
        phones = ','.join(item)
        print(phones)
        reg = send_multimsg_bydhst(phones, content, sign='【来财商贸】')
        if reg==0:
            tnum += len(item)
        item = list(itertools.islice(phone_list, 500))
    return tnum