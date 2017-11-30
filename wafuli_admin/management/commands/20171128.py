
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
from account.models import MyUser, ApplyLog
from django.db.models import F, Sum
import datetime
from django.core.management.base import BaseCommand
from public.pinyin import PinYin
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        users = MyUser.objects.all()
        for user in users:
            user.cs_qq = user.qq_number
            user.domain_name = user.qq_number
            user.save()
        for user in users:
            try:
                applog = ApplyLog.objects.get(mobile=user.mobile)
                user.qq_number = applog.qq_number
                user.save()
            except:
                continue
            

            
