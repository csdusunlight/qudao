'''
Created on 20160417

@author: zhlvch
'''

import logging
import time,datetime
from django.db import connection
from django.db.models import Sum, Count,Avg
from wafuli.models import Project, WithdrawLog, InvestLog
from statistic.models import UserDetailStatis
logger = logging.getLogger("wafuli")
from django.core.management.base import BaseCommand, CommandError
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Statistics is beginning*********")
        begin_time = time.time()
        today = datetime.date.today()
        
        yesterday = today - datetime.timedelta(days=1)
        
        cursor = connection.cursor()
        cursor.execute("select a.user_id, count(*), sum(a.return_amount), sum(a.invest_amount), \
                count(distinct a.project_id) from wafuli_investlog a where a.audit_time>='%s' and  \
                audit_state='0' group by a.user_id" % str(today) )

        row = cursor.fetchall()
        bulk_list = []
        for item in row:
            id = item[0]
            item_count = item[1]
            return_amount = item[2]
            invest_amount = item[3]
            project_count = item[4]
            item = UserDetailStatis(user_id=id, item_count=item_count, return_amount=return_amount, 
                                    invest_amount=invest_amount, project_count=project_count)
            bulk_list.append(item)
        UserDetailStatis.objects.bulk_create(bulk_list)
        
        cursor.execute("select a.user_id, count(*), sum(a.return_amount), sum(a.invest_amount), \
                count(distinct a.project_id) from wafuli_investlog a where a.audit_time>='%s' and  \
                audit_state='0' group by a.user_id" % str(today) )

        row = cursor.fetchall()
        bulk_list = []
        for item in row:
            id = item[0]
            item_count = item[1]
            return_amount = item[2]
            invest_amount = item[3]
            project_count = item[4]
            item = UserDetailStatis(user_id=id, item_count=item_count, return_amount=return_amount, 
                                    invest_amount=invest_amount, project_count=project_count)
            bulk_list.append(item)
        UserDetailStatis.objects.bulk_create(bulk_list)    
        
        end_time = time.time()
        logger.info("******Statistics is finished, time:%s*********",end_time-begin_time)
