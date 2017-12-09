#coding:utf-8
'''
Created on 2017年11月24日

@author: lch
'''
from wafuli_admin.models import Dict
from weixin.settings import submit_investlog_notify_templateid,\
    book_invest_notify_templateid, withdraw_success_notify_templateid,\
    withdraw_apply_notify_templateid
from dragon.settings import APPID, FULIUNION_DOMAIN
from weixin.models import WeiXinUser
from account.varify import httpconn
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
            amount = investlog.invest_amount
            term = investlog.invest_term
            openid = wuser.openid
            data = {'first':{'value':u"您的主页有用户成功交单，请及时处理。", 'color':"#173177"},
                    'keyword1':{'value':project, 'color':"#173177"},
                    'keyword2':{'value':str(amount) + u"元", 'color':"#173177"},
                    'keyword3':{'value':term, 'color':"#173177"},
                    'remark':{'value':u'如果您不想再收到此类通知，可在个人中心设置里取消微信消息通知', 'color':"#173177"},}
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
                    'remark':{'value':u'如果您不想再收到此类通知，可在个人中心设置里取消微信消息通知', 'color':"#173177"},}
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
            amount = str(withdrawlog.amount)
            balance = str(user.balance)
            withtime = withdrawlog.submit_time.strftime('%Y-%m-%d %H:%M')
            openid = wuser.openid
            data = {'first':{'value':u"福利联盟账户余额（自动）提现通知", 'color':"#173177"},
                    'keyword1':{'value':amount, 'color':"#173177"},
                    'keyword2':{'value':balance, 'color':"#173177"},
                    'keyword3':{'value':withtime, 'color':"#173177"},
                    'remark':{'value':u'如果您不想再收到此类通知，可在个人中心设置里取消微信消息通知', 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)
    elif type == 'withdraw_success':
        kwarg.update(template_id=withdraw_success_notify_templateid)
        for user_withdrawlog in user_obj_list:
            user = user_withdrawlog[0]
            withdrawlog = user_withdrawlog[1]
            wuser = user.weixin_users.first()
            if not wuser:
                continue
            amount = str(withdrawlog.amount)
            balance = str(user.balance)
            audittime = withdrawlog.audit_time.strftime('%Y-%m-%d %H:%M')
            bank = user.user_bankcard.first()
            openid = wuser.openid
            data = {'first':{'value':u"提现成功，请查收", 'color':"#173177"},
                    'keyword1':{'value':bank.bank, 'color':"#173177"},
                    'keyword2':{'value':bank.card_number, 'color':"#173177"},
                    'keyword3':{'value':bank.real_name, 'color':"#173177"},
                    'keyword2':{'value':amount, 'color':"#173177"},
                    'keyword3':{'value':audittime, 'color':"#173177"},
                    'remark':{'value':u'如果您不想再收到此类通知，可在个人中心设置里取消微信消息通知', 'color':"#173177"},}
            kwarg.update(data=data, touser=openid)
            ret = httpconn(url, kwarg, 1)
            logger.info(ret)