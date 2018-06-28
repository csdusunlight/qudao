
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
from wafuli.models import Project
from account.varify import sendmsg_bydhst, send_multimsg_bydhst
from account.models import MyUser, AdminPermission
class Command(BaseCommand):
    def handle(self, *args, **options):
        permisson = AdminPermission.objects.get(code='100')
        permisson.user_set.update(is_merchant='1')

            
