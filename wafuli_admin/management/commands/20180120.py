
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
from docs.models import Document
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        Project.objects.filter(is_official=True).update(category='official')
        Project.objects.filter(is_official=False).update(category='self')
        InvestLog.objects.filter(is_official=True).update(category='official')
        InvestLog.objects.filter(is_official=False).update(category='self')
            

            
