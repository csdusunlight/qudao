
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
from wafuli.models import Project
from django.core.cache import cache
import time
class Command(BaseCommand):
    def handle(self, *args, **options):
#         cache.set('lch',5)
        with cache.lock('lch',1):
            time.sleep(2)
#             cache.set('lch',12)
#             print cache.get('lch')
            for i in range(5):
                print i

            
