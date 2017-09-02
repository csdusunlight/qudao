
#coding:utf-8
'''
Created on 2017年2月19日

@author: lch
'''

from django.core.management.base import BaseCommand
import logging
from wafuli.models import UserEvent, Finance
from django.contrib.contenttypes.models import ContentType
from wafuli_admin.models import Invest_Record
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        finance_type = ContentType.objects.get_for_model(Finance)
        events = UserEvent.objects.filter(event_type='1',content_type = finance_type,audit_state='0')
        create_list = []
        for event in events:
            user = event.user
            translist = event.translist.first()
            project = event.content_object
            item = Invest_Record(invest_date = event.time, invest_company = project.company.name, 
                          qq_number = '', user_name = user.username, zhifubao = user.zhifubao, 
                          invest_mobile = event.invest_account, invest_period =event.invest_term, 
                          invest_amount = event.invest_amount, return_amount = translist.transAmount, 
                          wafuli_account = user.mobile,return_date = event.audit_time,is_futou = project.is_futou, 
                          coupon = '', remark ='')
            create_list.append(item)
        Invest_Record.objects.bulk_create(create_list)
