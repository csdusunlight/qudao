'''
Created on 20160417

@author: zhlvch
'''

import logging
import time,datetime
from django.db.models import Sum, Count,Avg
from activity.models import IPAward, IPLog, SubmitRank
from account.models import MyUser
logger = logging.getLogger("wafuli")
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Activity Statistics is beginning*********")
        begin_time = time.time()
        today = datetime.date.today()
        
        item_list = IPLog.objects.filter(award__gt=0).values('user').\
            annotate(cou=Count('*'),award=Sum('award')).order_by('user')
        for dic in item_list:
            user_id = dic.get('user')
            count = dic.get('cou')
            award = dic.get('award') or 0
            user=MyUser.objects.get(id=user_id)
            SubmitRank.objects.update_or_create(user=user,defaults={'award':award,'sub_num':count})
        ranks = SubmitRank.objects.all().order_by("-sub_num")
        i = 1
        n = 0
        j = 0
        for r in ranks:
            if r.acc_num == n:
                r.rank = i
            else:
                i = i + j
                r.rank = i
                j = 0
            j = j + 1
            n = r.acc_num
            r.save(update_fields=['rank'])
        
        end_time = time.time()
        logger.info("******Activity is finished, time:%s*********",end_time-begin_time)
