
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
import logging
from wafuli.models import *
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum,F
from account.models import MyUser, Channel
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
#from project_admin.models import ProjectStatis, DayStatis, Project,\
#    ProjectInvestData, AccountBill, Account, DayAccountStatic
import logging
import time
logger = logging.getLogger("wafuli")
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         logger.info("******Project_statis is beginning*********")
#         begin_time = time.time()
#         today = datetime.date.today()
#         from django.db import connection, transaction
#         cursor = connection.cursor()
#         cursor.execute("select a.project_id, a.source, sum(a.settle_amount) as sumofsettle, \
#                             sum(a.return_amount) as sumofret from project_admin_projectinvestdata a \
#                             group by a.project_id, a.source")
#         # 数据修改操作——提交要求
# #         cursor.execute("select b.is_channel,  a.audit_state,  \
# #             sum(invest_amount) as sum, count(*) as count from wafuli_userevent a join account_myuser b\
# #              on a.user_id=b.id group by a.audit_state, b.is_channel")
# #         transaction.commit_unless_managed()

#         # 数据检索操作,不需要提交
# #         cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#         row = cursor.fetchall()
#         project_dic = {}
#         for item in row:
#             id = item[0]
#             source = item[1]
#             consume = item[2]
#             ret = item[3]
#             attr = {}
#             if project_dic.has_key(id):
#                 attr = project_dic[id]
#             else:
#                 project_dic[id] = attr
#             if source == 'site':
#                 attr['site_consume'] = consume
#                 attr['site_return'] = ret
#             elif source == 'channel':
#                 attr['channel_consume'] = consume
#                 attr['channel_return'] = ret
# #         print project_dic
#         for id, kwarg in project_dic.items():
#             obj,created = ProjectStatis.objects.update_or_create(project_id=id, defaults=kwarg)
#             Project.objects.filter(id=id).update(consume=obj.consume())
# #         return row
#         update_fields = {}
#         update_fields['start_num'] = Project.objects.filter(state='start').count()
#         update_fields['finish_num'] = Project.objects.filter(state='finish').count()
#         update_fields['invest_count'] = ProjectInvestData.objects.filter(invest_time=today).count()
#         statdic = ProjectInvestData.objects.filter(invest_time=today).aggregate(invest_sum=Sum('invest_amount'),
#                consume_sum=Sum('settle_amount'))
#         update_fields['ret_count'] = ProjectInvestData.objects.filter(invest_time=today, state='0').count()
#         statdic_pass = ProjectInvestData.objects.filter(invest_time=today, state='0').aggregate(
#                ret_invest_sum=Sum('invest_amount'), ret_sum=Sum('return_amount'))
#         update_fields.update(statdic)
#         update_fields.update(statdic_pass)
#         obj, created = DayStatis.objects.update_or_create(date=today, defaults=update_fields)
# #         cursor.execute("select a.project_id, a.source, sum(a.settle_amount) as sumofsettle, \
# #                             sum(a.return_amount) as sumofret from project_admin_projectinvestdata a \
# #                             group by a.project_id, a.source")
#         update_fields = {}
#         income = AccountBill.objects.filter(time__gte=today, type='income').aggregate(income=Sum('amount'))
#         expenditure = AccountBill.objects.filter(time__gte=today, type='expend').aggregate(expenditure=Sum('amount'))
#         balance = Account.objects.aggregate(balance=Sum('balance'))
#         update_fields.update(income)
#         update_fields.update(expenditure)
#         update_fields.update(balance)
#         obj, created = DayAccountStatic.objects.update_or_create(date=today, defaults=update_fields)

#         end_time = time.time()
#         logger.info("******Project_statis is finished, time:%s*********",end_time-begin_time)
