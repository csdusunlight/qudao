
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum,F
from account.models import MyUser, Channel
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
from wafuli_admin.models import RecommendRank, DayStatis
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        finance_type = ContentType.objects.get_for_model(Finance)
        UserEvent.objects.filter(content_type=finance_type).update(invest_time = F('time'))
