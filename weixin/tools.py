#coding:utf-8
'''
Created on 2017年11月24日

@author: lch
'''
from wafuli_admin.models import Dict
from weixin.settings import submit_investlog_notify_templateid,\
    book_invest_notify_templateid
from dragon.settings import APPID, FULIUNION_DOMAIN
from weixin.models import WeiXinUser
from account.varify import httpconn
import logging
logger = logging.getLogger('wafuli')
def sendWeixinNotify(user_obj_list, type):
    access_token = Dict.objects.get(key='access_token')
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