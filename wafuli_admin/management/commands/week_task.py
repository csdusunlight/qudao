'''
Created on 20160608

@author: lch
'''
import logging
from django.core.management.base import BaseCommand
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******WeekTask is beginning*********")
        logger.info("******WeekTask is finished*********")