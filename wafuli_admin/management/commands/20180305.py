
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
from merchant.models import Margin_Translog
logger = logging.getLogger("wafuli")
from wafuli.models import InvestLog, TransList
class Command(BaseCommand):
    def handle(self, *args, **options):
        ts = Margin_Translog.objects.filter(reason=u"佣金")
        for t in ts:
            if t.auditlog and t.auditlog.broker_amount==0 and t.transAmount!=0:
                print t.transAmount,t.auditlog.broker_amount
                t.auditlog.broker_amount = t.transAmount
#                 t.auditlog.save()
            

            
