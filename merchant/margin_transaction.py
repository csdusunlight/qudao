#coding:utf-8
'''
Created on 20160318

@author: lch
'''
#type_add = '0'
#type_min = '1'
from account.models import MyUser
import logging
from django.db import transaction
from django.db.models import F
from decimal import Decimal
from merchant.models import Margin_Translog
logger = logging.getLogger('wafuli')
class ChargeValueError(ValueError):
    def __init__(self, err):
        Exception.__init__(self,err)
        
def charge_margin(user, type, amount, reason, reverse=False, remark='', auditlog=None):
    if not (isinstance(user, MyUser) and reason) or type !='0' and type != '1':
        raise ChargeValueError('Charge_money Parameters ERROR!!!')
    amount = Decimal(amount)
    if amount <= 0:
        raise ChargeValueError('Charge_money amount can not be less or equal to 0')
    with transaction.atomic():
        user = MyUser.objects.get(id=user.id)
        trans = Margin_Translog.objects.create(user=user, transType=type, initAmount = user.margin_account,
                          transAmount=amount, reason=reason, remark=remark, auditlog=auditlog)
        if type == '0':
            user.margin_account = F('margin_account') + amount
            user.save(update_fields=['margin_account'])
        elif user.margin_account < amount:
            raise ChargeValueError(u'账号 ' + user.mobile + u'中的资金余额不足，请先充值！')
        else:
            user.margin_account = F('margin_account') - amount
            user.save(update_fields=['margin_account'])

        return trans