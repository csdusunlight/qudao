#coding:utf-8
'''
Created on 2016年8月29日

@author: lch
'''
import logging
from django.core.management.base import BaseCommand
from django.db.models import F
import datetime
import time
from wafuli.models import InvestLog, Company
from django.db.models.aggregates import Count
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Day-task is beginning*********")
        begin_time = time.time()
        sevent_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        ret =InvestLog.objects.filter(submit_time__gte=sevent_days_ago, project__state__in=['10','20']).values('project__company_id').\
            annotate(count=Count('id')).order_by('project__company_id')
        for item in ret:
            print item
            cid = item['project__company_id']
            try:
                company = Company.objects.get(id=cid)
                company.view_count = item['count']
                company.save(update_fields="view_count")
            except:
                pass
        end_time = time.time()
        logger.info("******Day-task is finished, time:%s*********",end_time-begin_time)