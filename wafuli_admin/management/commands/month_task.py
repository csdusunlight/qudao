'''
Created on 20160608

@author: lch
'''
import logging
from wafuli.models import UserEvent
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
from wafuli_admin.models import RecommendRank, UserStatis
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******MonthTask  is beginning*********")
        month = ttime.localtime()[1]-1 or 12
        year = ttime.localtime()[0]
        year = year-1 if month == 12 else year
        inviters = MyUser.objects.all()
        for inviter in inviters:
            invite_lastmonth = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                        audit_state='0',audit_time__year=year,audit_time__month=month).\
                        aggregate(sumofwith=Sum('invest_amount'))
            award_lastmonth = float(invite_lastmonth.get('sumofwith') or 0)*settings.AWARD_RATE
            award_lastmonth = int(award_lastmonth)
            inviter.invite_account += award_lastmonth
            inviter.invite_income += award_lastmonth
            inviter.save(update_fields=['invite_account','invite_income'])

        # trunscate table RecommendRank
        RecommendRank.objects.all().delete()
        
        UserStatis.objects.update(month_statis=0)
        
        logger.info("******MonthTask is finished*********")