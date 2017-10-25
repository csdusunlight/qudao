
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
from account.models import MyUser
from django.db.models import F, Sum
import datetime
from django.core.management.base import BaseCommand
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.all()
        for p in projects:
            p.points = InvestLog.objects.filter(project=p).count()
            p.save()
