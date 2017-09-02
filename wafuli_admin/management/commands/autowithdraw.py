
#coding:utf-8
'''
Created on 2017年6月14日

@author: lch
'''
import logging
import time
from django.core.management.base import BaseCommand
from account.models import MyUser, Channel
from account.transaction import charge_money
from wafuli.models import UserEvent
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Auto-withdrawing is beginning*********")
        begin_time = time.time()
        channels = Channel.objects.filter(user__balance__gte=50000)
        for ch in channels:
            user = ch.user
            card = user.user_bankcard.first()
            if not card:
                continue
            translist = charge_money(user, '1', user.balance, u'系统自动提现')
            if translist:
                event = UserEvent.objects.create(user=user, event_type='2', invest_account=card.card_number,
                            invest_amount=user.balance, audit_state='1')
                translist.user_event = event
                translist.save(update_fields=['user_event'])
        end_time = time.time()
        logger.info("******Auto-withdrawing is finished, time:%s*********",end_time-begin_time)