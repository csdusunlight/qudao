#coding:utf-8
import datetime

import logging
from django.utils import timezone
from django.db import transaction
from newsm.models import Article

logger = logging.getLogger('wafuli')


from celery import  shared_task

@shared_task
def async_1hour_article_state(self):
    current_time=timezone.now()
    aimobj=Article.objects.filter(apub_date__lte=current_time)
    for i in aimobj:
        i.ais_published='1'
        i.save()
