
#coding:utf-8
'''
Created on 2017年6月14日

@author: lch
'''
import logging
import time
from django.core.management.base import BaseCommand
from account.models import MyUser
from account.transaction import charge_money
from wafuli.models import WithdrawLog
from django.db import transaction
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Auto-withdrawing is beginning*********")
        begin_time = time.time()
        channels = MyUser.objects.filter(balance__gte=10)
        for user in channels:
            card = user.user_bankcard.first()
            if not card:
                continue
            with transaction.atomic():
                charge_money(user, '1', user.balance, u'系统自动提现')
                WithdrawLog.objects.create(user=user, amount=user.balance, audit_state='1')
        end_time = time.time()
        logger.info("******Auto-withdrawing is finished, time:%s*********",end_time-begin_time)