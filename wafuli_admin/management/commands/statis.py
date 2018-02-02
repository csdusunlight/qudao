#coding:utf-8
'''
Created on 20160417

@author: zhlvch
'''

import logging
import time,datetime
from django.db import connection
from django.db.models import Sum, Count,Avg,F
from wafuli.models import Project, WithdrawLog, InvestLog
from activity.models import IPAward, IPLog
from docs.models import Document, DocStatis
from django.core.cache import cache
from public.redis import cache_decr_or_set
logger = logging.getLogger("wafuli")
from django.core.management.base import BaseCommand, CommandError
from account.models import MyUser, Userlogin, ApplyLog
from wafuli_admin.models import DayStatis, GlobalStatis
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Statistics is beginning*********")
        begin_time = time.time()
        today = datetime.date.today() 
        yesterday = today - datetime.timedelta(days=1)
        apply_num = ApplyLog.objects.filter(submit_time__gte=today).count()
        refuse_num = ApplyLog.objects.filter(audit_time__gte=today,audit_state='2').count()
        new_reg_num = ApplyLog.objects.filter(audit_time__gte=today,audit_state='0').count()
        dict = WithdrawLog.objects.filter(audit_time__gte=today, audit_state='0').\
                aggregate(cou=Count('user_id',distinct=True),sum=Sum('amount'))
        with_amount = dict.get('sum') or 0
        with_num = dict.get('cou')
        dict = InvestLog.objects.filter(audit_time__gte=today,audit_state='0').\
                aggregate(cou=Count('user_id',distinct=True),sum1=Sum('settle_amount'),sum2=Sum('invest_amount'))
        ret_amount = dict.get('sum1') or 0
        invest_amount = dict.get('sum2') or 0
        ret_num = dict.get('cou')
        
        new_project_num = Project.objects.filter(pub_date__gte=today).count()
        
#         dict = IPLog.objects.filter(time__gte=today).aggregate(total=Sum('award'))
#         activity_consume = dict.get('total')
        
        update_fields = {
                        'apply_num':apply_num,
                        'refuse_num':refuse_num,
                        'new_reg_num':new_reg_num,
                        'with_amount':with_amount,
                        'with_num':with_num,
                        'ret_amount':ret_amount,
                        'invest_amount':invest_amount,
                        'ret_num':ret_num,
                        'new_project_num':new_project_num,
#                         'activity_consume':activity_consume
        }
        DayStatis.objects.update_or_create(date=today, defaults=update_fields)
        
        first_day = datetime.datetime(today.year, today.month, 1)
        
        with_total = MyUser.objects.aggregate(sum=Sum('with_total'))
        invest_total = InvestLog.objects.filter(audit_state='0').aggregate(sum=Sum('invest_amount'),
                            count=Count('*'))
        global_statis = GlobalStatis.objects.first()
        if not global_statis:
            global_statis = GlobalStatis()
        global_statis.all_wel_num = Project.objects.count()
        global_statis.with_total = ((with_total.get('sum') or 0) + 91630000)/10000
        global_statis.invest_total = ((invest_total.get('sum') or 0) + 4836240000)/10000
        global_statis.user_total = MyUser.objects.count() + 300
        global_statis.invite_total = (invest_total.get('count') or 0) + 4180000
        global_statis.save()
        
        #文档定时关闭
        Document.objects.filter(close_time__lte=datetime.datetime.now(), is_on=True).update(is_on=False, close_time=None)
        
        #文档访问次数持久化
        keys_list = cache.keys('doc_*')
        kv_dict = cache.get_many(keys_list)
        for k,v in kv_dict.items():
            if v > 0:
                id = k[4:]
                doc = Document.objects.filter(id=id).first()
                if doc:
                    obj, created = DocStatis.objects.get_or_create(date=today, doc_id=id)
                    doc.view_count = F('view_count')+v
                    obj.view_count = F('count')+v
                    doc.save(update_fields=['view_count',])
                    obj.save(update_fields=['count',])
                    cache_decr_or_set(k, v)
                    cache.expire(k, 24*60*60)
                else:
                    cache.delete(k)
        
        end_time = time.time()
        logger.info("******Statistics is finished, time:%s*********",end_time-begin_time)
