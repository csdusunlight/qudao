
#coding:utf-8
'''
Created on 2016年8月13日

@author: lch
'''
import logging
from wafuli.models import *
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum,F
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
from wafuli_admin.models import RecommendRank, DayStatis
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        wels = Welfare.objects.all()
        wels.update(exp_url_pc=F("exp_url"),exp_url_mobile=F("exp_url"))
        
        wels = Task.objects.all()
        wels.update(exp_url_pc=F("exp_url"),exp_url_mobile=F("exp_url"))
        
        wels = Finance.objects.all()
        wels.update(exp_url_pc=F("exp_url"),exp_url_mobile=F("exp_url"))
