
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
from account.models import MyUser
from django.db.models import F, Sum
import datetime
from django.core.management.base import BaseCommand
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        item_list = WithdrawLog.objects.filter(audit_state='0').values('user').\
            annotate(award=Sum('amount')).order_by('user')
        for dic in item_list:
            user_id = dic.get('user')
            award = dic.get('award') or 0
            user=MyUser.objects.get(id=user_id)
            user.with_total = award
            user.save()
#             RecommendRank.objects.update_or_create(user=user,defaults={'award':award,'acc_num':count})
