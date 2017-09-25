'''
Created on 20160318

@author: lch
'''
#type_add = '0'
#type_min = '1'
from wafuli.models import TransList
from account.models import MyUser
import logging
from django.db import transaction
from django.db.models import F
from decimal import Decimal
logger = logging.getLogger('wafuli')

def charge_money(user, type, amount, reason, reverse=False):
    if not (isinstance(user, MyUser) and reason) or type !='0' and type != '1':
        raise Exception('Charge_money Parameters ERROR!!!')
    amount = Decimal(amount)
    if amount <= 0:
        raise Exception('Charge_money amount can not be less or equal to 0')
    with transaction.atomic():
        trans = TransList.objects.create(user=user, transType=type, initAmount = user.balance, 
                          transAmount=amount, reason=reason)
        if type == '0':
            user.balance = F('balance') + amount
            if not reverse:
                user.accu_income = F('accu_income') + amount
            user.save(update_fields=['accu_income','balance'])
        elif user.balance < amount:
            raise ValueError('The account ' + user.mobile + '\'s balance is not enough!')
        else:
            user.balance = F('balance') - amount
            if reverse:
                user.accu_income = F('accu_income') - amount
            user.save(update_fields=['accu_income','balance'])

        return trans
