#coding:utf-8
'''
Created on 2017年11月24日

@author: lch
'''
import datetime

import logging

from django.db import transaction

from account.transaction import charge_money
from finance.pay import batch_transfer_to_zhifubao
from wafuli.models import InvestLog

logger = logging.getLogger('wafuli')


from celery import shared_task  

@shared_task
def async_batch_transfer_task(investlog_list):
    batch_list = []
    id_list = []
    for obj in investlog_list:
        id_list.append(obj.id)
        batch_list.append({
            'obj': obj,
            'payee_account': obj.zhifubao,
            'payee_real_name': obj.zhifubao_name,
            'amount': str(obj.return_amount),
            'remark': obj.project.title,
            'payer_name': u'%s（%s）' % (obj.user.qq_name, obj.user.qq_number)
        })
    ret = batch_transfer_to_zhifubao(batch_list, 'fulio', u'做单返现')
    fail_id_list = []
    for item in ret['detail']:
        obj = item['obj']
        fail_id_list.append(obj.id)
        with transaction.atomic():
            obj.pay_reason = item['msg']
            obj.pay_state = '4'
            obj.save(update_fields=['pay_reason','pay_state'])
            charge_money(obj.user, '0', obj.return_amount, u'冲账', True, u"打款转账失败", auditlog=obj)
    # print(id_list)
    # print(fail_id_list)
    suc_list = [i for i in id_list if i not in fail_id_list]
    # print(suc_list)
    InvestLog.objects.filter(id__in=suc_list).update(pay_state='3', pay_time=datetime.datetime.now())
