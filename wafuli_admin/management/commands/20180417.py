
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
class Command(BaseCommand):
    def handle(self, *args, **options):
        coupons = UserCoupon.objects.filter(state='0')
        for coupon in coupons:
            coupon.checklock()

            
