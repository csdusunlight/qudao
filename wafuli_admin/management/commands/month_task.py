'''
Created on 20160608

@author: lch
'''
import logging
from wafuli.models import InvestLog
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
import datetime
from statistic.models import PerformanceStatistics
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******MonthTask  is beginning*********")
        last_month = ttime.localtime()[1]-1 or 12
        last_year = ttime.localtime()[0]
        last_year = last_year-1 if last_month == 12 else last_year
        last2_month = last_month-1 or 12
        last2_year = last_year-1 if last2_month == 12 else last_year
        last3_month = last2_month-1 or 12 
        last3_year = last2_year-1 if last3_month == 12 else last2_year
        print last_year, last_month, last2_year, last2_month, last3_year, last3_month
        firstday_lastmonth = datetime.date(last_year, last_month, 1)
        firstday_last2month = datetime.date(last2_year, last2_month, 1)
        firstday_last3month = datetime.date(last3_year, last3_month, 1)
        firstday_thismonth = datetime.date(ttime.localtime()[0],ttime.localtime()[1],1)
        lastday_lastmonth = firstday_thismonth - datetime.timedelta(days=1)
        invitees = MyUser.objects.filter(inviter__isnull=False, date_joined__gt=firstday_last3month)
        inviters = {}
        for invitee in invitees:
            inviter = invitee.inviter
            enddate  = lastday_lastmonth
            if enddate > (invitee.date_joined + datetime.timedelta(days=60)).date():            
                enddate = (invitee.date_joined + datetime.timedelta(days=60)).date()
            sum = InvestLog.objects.filter(user=invitee, is_official=True, audit_state='0', audit_time__range=(firstday_lastmonth,
                    enddate)).aggregate(sum=Sum('settle_amount'))
            settle_amount = sum.get('sum') or 0
            if inviter.id in inviters:
                inviters[inviter.id] += settle_amount
            else:
                inviters[inviter.id] = settle_amount
            
        print inviters
        for inviter, amount in inviters.items():
            PerformanceStatistics.objects.create(startdate = firstday_lastmonth, enddate=lastday_lastmonth, user_id=inviter,
                                  amount=amount)
        
        
        logger.info("******MonthTask is finished*********")