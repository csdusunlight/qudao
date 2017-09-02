#coding:utf-8
'''
Created on 2016年8月29日

@author: lch
'''
import logging
from wafuli.models import Welfare, UserTask, Coupon, CouponProject
from django.core.management.base import BaseCommand
from account.models import MyUser, UserToken
from django.db.models import F
import datetime
import time
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Day-task is beginning*********")
        begin_time = time.time()
        usertasks = UserTask.objects.all()
        for usertask in usertasks:
            task = usertask.task
            task.left_num = F("left_num")+1
            task.save(update_fields=['left_num'])
            usertask.delete()
            
        projects = CouponProject.objects.filter(endtime__lte=datetime.date.today()).order_by()
        for project in projects:
            if project.ctype == '2':
                project.coupons.all().delete()
            else:
                project.coupons.filter(is_used=False).delete()
                
        UserToken.objects.filter(expire<time.time()*1000).delete()
        end_time = time.time()
        logger.info("******Day-task is finished, time:%s*********",end_time-begin_time)