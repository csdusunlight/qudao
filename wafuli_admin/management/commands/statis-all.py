'''
Created on 20160417

@author: zhlvch
'''

import logging
import time
import datetime
from wafuli_admin.models import DayStatis
from django.db import connection
from django.db.models import Sum, Count,Avg
logger = logging.getLogger("wafuli")
from django.core.management.base import BaseCommand, CommandError
from account.models import MyUser
from account.models import Userlogin
from wafuli.models import UserEvent
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Statistics-all  is beginning*********")
        begin_time = time.time()
        events = MyUser.objects.all()
        for e in events:
            e.accu_income =0
            e.accu_scores =0
            e.invite_income =0
            e.invite_scores =0
            e.balance =0
            e.scores=0
            e.save()
        date_list = MyUser.objects.dates('date_joined', 'day', order='DESC')
        print date_list
        select = {'day': connection.ops.date_trunc_sql('day', 'date_joined')}
        dict_list = MyUser.objects.extra(select=select).values('day').annotate(count=Count('id')).order_by('-day')
        for dict in dict_list:
            print dict
            day = dict.get('day')
            date = day.date()
            obj, created = DayStatis.objects.update_or_create(date=date,defaults={'new_reg_num':dict.get('count')})
        select = {'day': connection.ops.date_trunc_sql('day', 'time')}
        dict_list = Userlogin.objects.extra(select=select).values('day').annotate(num=Count('user',distinct=True)).order_by('-day')
        for dict in dict_list:
            day = dict.get('day')
            date = day.date()
            obj, created = DayStatis.objects.update_or_create(date=date,defaults={'active_num':dict.get('num')})
        select = {'day': connection.ops.date_trunc_sql('day', 'audit_time')}
        dict_list = UserEvent.objects.filter(event_type='2',audit_state='0').extra(select=select).values('day').\
                annotate(cou=Count('user_id',distinct=True),sum=Sum('invest_amount')).order_by('-day')
        for dict in dict_list:
            day = dict.get('day')
            date = day.date()
            update_fields = {'with_num':dict.get('cou'),'with_amount':dict.get('sum') or 0}
            obj, created = DayStatis.objects.update_or_create(date=date,defaults=update_fields)
        dict_list = UserEvent.objects.filter(event_type='1',audit_state='0').extra(select=select).values('day').\
                annotate(cou=Count('user_id',distinct=True),sum1=Sum('translist__transAmount'),\
                         sum2=Sum('score_translist__transAmount')).order_by('-day')
        for dict in dict_list:
            day = dict.get('day')
            date = day.date()
            update_fields = {'ret_num':dict.get('cou'),'ret_amount':dict.get('sum1') or 0,'ret_scores':dict.get('sum2') or 0}
            obj, created = DayStatis.objects.update_or_create(date=date,defaults=update_fields)
        dict_list = UserEvent.objects.filter(event_type='3',audit_state='0').extra(select=select).values('day').\
                annotate(cou=Count('user_id',distinct=True),sum=Sum('invest_amount')).order_by('-day')
        for dict in dict_list:
            day = dict.get('day')
            date = day.date()
            update_fields = {'exchange_num':dict.get('cou'),'exchange_scores':dict.get('sum') or 0}
            obj, created = DayStatis.objects.update_or_create(date=date,defaults=update_fields)
#         print MyUser.objects.values('inviter').annotate(cou=Count('*'),sum=Sum('inviter__balance'))
#         print MyUser.objects.filter(inviter__isnull=False)
        end_time = time.time()
#         select = {'day': connection.ops.date_trunc_sql('day', 'date_joined')}
#         print MyUser.objects.extra(select=select).values('day').annotate(num=Count("*"))
#         select = {'day': connection.ops.date_trunc_sql('day', 'last_login_time')}
#         print MyUser.objects.extra(select=select).values('day').annotate(num=Count("*"))
        logger.info("******Statistics-all is finished, time:%s*********",end_time-begin_time)