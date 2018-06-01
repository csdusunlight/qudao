#coding:utf-8
'''
Created on 2018年5月31日

@author: lch
'''
from coupon.models import Contract, UserCoupon
from account.signals import register_signal

def my_signal_handler(sender, **kwargs):
    user = kwargs.get('user')
    contracts = Contract.objects.filter(name__startswith=u"新手红包")
    bulks = []
    for con in contracts:
        bulk = UserCoupon(type='heyue', user=user, contract=con, award=con.award)
        bulks.append(bulk)
    bulks.append(UserCoupon(type='guanzhu', user=user, award=1))
    bulks.append(UserCoupon(type='bangka', user=user, award=2))
    bulks.append(UserCoupon(type='shoudan', user=user, award=5))
    UserCoupon.objects.bulk_create(bulks)
register_signal.connect(my_signal_handler, dispatch_uid="register")