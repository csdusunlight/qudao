
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
from wafuli.models import Project
class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.filter(is_official=False).update(category='self')

            
