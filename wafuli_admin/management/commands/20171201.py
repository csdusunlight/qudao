
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
from account.models import MyUser, ApplyLog
from django.db.models import F, Sum
import datetime
from django.core.management.base import BaseCommand
from public.pinyin import PinYin
from docs.models import Document
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        docs = Document.objects.all()
        for doc in docs:
            content = doc.content
            content = content.replace('_self', '_blank')
            doc.content = content
            doc.save()
            

            
