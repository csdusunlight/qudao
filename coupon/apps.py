#coding:utf-8
'''
Created on 2018年5月31日

@author: lch
'''
from django.apps.config import AppConfig
from django.dispatch import receiver
from django.core.signals import request_finished
from account.signals import register_signal

class CouponAppConfig(AppConfig):
    name = 'coupon'
    verbose_name = u"优惠券"
    def ready(self):
#         @receiver(request_finished, dispatch_uid="request_finished")
        import coupon.signals