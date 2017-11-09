
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
        users = MyUser.objects.filter(balance__gte=10, is_autowith=True)
        for user in users:
            card = user.user_bankcard.first()
            if not card:
                continue
            with transaction.atomic():
                amount = user.balance
                charge_money(user, '1', amount, u'系统自动提现')
                WithdrawLog.objects.create(user=user, amount=amount, audit_state='1')
        end_time = time.time()
        logger.info("******Auto-withdrawing is finished, time:%s*********",end_time-begin_time)