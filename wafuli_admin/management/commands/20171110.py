
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
from public.pinyin import PinYin
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        projects=Project.objects.all()
        pyin = PinYin()
        pyin.load_word()
        for project in projects:
            title = project.title
            szm, pinyin = pyin.hanzi2pinyin_split(title)
            project.szm = szm
            project.pinyin = pinyin
            project.save()
            

            
