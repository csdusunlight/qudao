#coding:utf-8
'''
Created on 20160306

@author: lch
'''
from random import Random
import smtplib  
from email.mime.text import MIMEText  
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response
mail_host="smtp.126.com"  #设置服务器
mail_user="hunanjinyezi@126.com"    #用户名
mail_pass="jinyezi520"   #口令 
mail_postfix="126.com"  #发件箱的后缀
import logging
logger = logging.getLogger('wafuli')
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
def get_page_no(x):
    try:
        x=int(x)
        return x if x > 0 else 1
    except ValueError:
        return 1

def send_mail(to_email, id):
    active_code = random_str(30) + str(id)
    active_addr = settings.DOMAIN_URL + reverse('active_email')+'?code='+active_code
    content_html = str( render_to_response("account/email_template.html", {'url':active_addr}))
    content_html = content_html[content_html.index('<meta content="text/html; charset=utf-8" />'):]
    content = content_html
    msg = MIMEText(content,_subtype='html',_charset='utf-8') #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = u'挖福利邮箱激活'    #设置主题
    msg['From'] = mail_user
    msg['To'] = to_email 
    try:  
        s = smtplib.SMTP()  
        s.connect(mail_host)  #连接smtp服务器
        s.login(mail_user,mail_pass)  #登陆服务器
        res = s.sendmail(mail_user, [to_email,], msg.as_string())  #发送邮件
        s.close()  
        return active_code
    except Exception, e:  
        logger.error(str(e))
        return ''
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip