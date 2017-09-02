'''
Created on 20160608

@author: lch
'''
import logging
from wafuli_admin.models import UserStatis
from django.core.management.base import BaseCommand
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******WeekTask is beginning*********")
        UserStatis.objects.update(week_statis=0)
        logger.info("******WeekTask is finished*********")