
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
from wafuli_admin.views import batch_withdraw_task
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Auto-withdrawing is beginning*********")
        begin_time = time.time()
        batch_withdraw_task()
        end_time = time.time()
        logger.info("******Auto-withdrawing is finished, time:%s*********",end_time-begin_time)