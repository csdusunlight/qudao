
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
from wafuli.models import Project
from account.varify import sendmsg_bydhst, send_multimsg_bydhst
from account.models import MyUser, AdminPermission
import datetime
class Command(BaseCommand):
    def handle(self, *args, **options):
        coupons = UserCoupon.objects.filter(start_date__isnull=True,type='heyue')
        for coupon in coupons:
            coupon.start_date = coupon.create_date
            coupon.save(update_fields=['start_date'])
        coupons = UserCoupon.objects.filter(expire__isnull=True,type='heyue')
        for coupon in coupons:
            contract = coupon.contract
            coupon.end_date = coupon.start_date + datetime.timedelta(days=contract.continue_days)
            coupon.save(update_fields=['end_date'])
            
            
