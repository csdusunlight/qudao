
#coding:utf-8
'''
Created on 2016年8月13日

@author: lch
'''
import logging
from wafuli.models import *
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
from wafuli_admin.models import RecommendRank, DayStatis
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        advs = Advertisement.objects.all()
        for adv in advs:
            Advertisement_Mobile.objects.create(mpic=adv.mpic,location=adv.location,
                    is_hidden=adv.is_hidden,navigation=adv.navigation,
                    title=adv.title,priority=adv.priority,
                    pub_date=adv.pub_date,view_count=adv.view_count,
                    change_user=adv.change_user,url=adv.url)