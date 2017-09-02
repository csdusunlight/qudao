
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
from wafuli_admin.models import RecommendRank, DayStatis, UserStatis
import datetime
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        finance_type = ContentType.objects.get_for_model(Finance)
        today = datetime.date.today() 
        first_day_month = datetime.datetime(today.year, today.month, 1)
        today = datetime.date.today()
        dayOfWeek = datetime.datetime.now().weekday()
        delta=datetime.timedelta(days=dayOfWeek)
        first_day_week = today - delta
        item_list = UserEvent.objects.filter(time__gte=first_day_week, event_type='2', audit_state='0').values('user').\
            annotate(award=Sum('translist__transAmount')).order_by('user')
        for dic in item_list:
            user_id = dic.get('user')
#             count = dic.get('cou')
            award = dic.get('award') or 0
            user=MyUser.objects.get(id=user_id)
            obj, created = UserStatis.objects.update_or_create(user=user, defaults={'week_statis':award})
        item_list = UserEvent.objects.filter(time__gte=first_day_month, event_type='2', audit_state='0').values('user').\
            annotate(award=Sum('translist__transAmount')).order_by('user')
        for dic in item_list:
            user_id = dic.get('user')
#             count = dic.get('cou')
            award = dic.get('award') or 0
            user=MyUser.objects.get(id=user_id)
            obj, created = UserStatis.objects.update_or_create(user=user, defaults={'month_statis':award})
#             RecommendRank.objects.update_or_create(user=user,defaults={'award':award,'acc_num':count})
