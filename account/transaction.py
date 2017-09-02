'''
Created on 20160318

@author: lch
'''
#type_add = '0'
#type_min = '1'
from wafuli.models import TransList, ScoreTranlist
from account.models import MyUser
import logging
from django.db import transaction
from django.db.models import F
logger = logging.getLogger('wafuli')
def charge_money(user, type, amount, reason, reverse=False):
    if not (isinstance(user, MyUser) and reason) or type !='0' and type != '1':
        return -1
    try:
        amount = int(amount)
    except:
        return None
    trans = None
    try:
        with transaction.atomic():
            user = MyUser.objects.get(id=user.id)
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
    except Exception, e:
        logger.info(e)
        return None
    else:
        return trans


def correct_money(user, type, amount, reason):
    pass

def charge_score(user, type, amount, reason):
    if not (isinstance(user, MyUser) and reason) or type !='0' and type != '1':
        return None
    try:
        amount = int(amount)
    except:
        return None
    trans = None
    try:
        with transaction.atomic():
            user = MyUser.objects.get(id=user.id)
            trans = ScoreTranlist.objects.create(user=user, transType=type, initAmount = user.scores, 
                              transAmount=amount, reason=reason)
            if type == '0':
                user.scores = F('scores') + amount
                user.accu_scores = F('accu_scores') + amount
                user.save(update_fields=['accu_scores','scores'])
            elif user.scores < amount:
                raise ValueError('The account ' + user.mobile + '\'s scores is not enough!')
            else:
                user.scores = F('scores') - amount
                user.save(update_fields=['scores'])
    except Exception, e:
        logger.info(e)
        return None
    else:
        return trans
    
def correct_score(user, type, amount):
    pass