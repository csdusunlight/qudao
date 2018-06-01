#coding:utf-8
'''
Created on 2018年5月31日

@author: lch
'''
from django.apps.config import AppConfig
from django.dispatch import receiver
from django.core.signals import request_finished

class AccountAppConfig(AppConfig):
    name = 'account'
    verbose_name = u"个人中心"
        