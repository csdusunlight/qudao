
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
import datetime
class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.all()
        for project in projects:
            url = project.strategy
            url = url.replace('51fanshu', '91fanshu')
            project.strategy = url
            project.save(update_fields=['strategy'])

            
            
