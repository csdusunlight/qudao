#coding:utf-8
'''
Created on 2018年5月31日

@author: lch
'''
from coupon.models import Contract, UserCoupon
from account.signals import register_signal
from account.varify import sendmsg_bydhst
import datetime

def my_signal_handler(sender, **kwargs):
    user = kwargs.get('user')
    contracts = Contract.objects.filter(name__startswith=u"新手红包")
    bulks = []
    for con in contracts:
        for contract in contracts:
            if contract.start_date:
                start_date = contract.start_date
            else:
                start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=contract.continue_days)
            expire = start_date + datetime.timedelta(days=contract.exipire_days)
            coupon = UserCoupon(user=user, contract=contract, type='heyue', expire=expire,
                                start_date=start_date, end_date=end_date, award=contract.award)
            bulks.append(coupon)
    bulks.append(UserCoupon(type='guanzhu', user=user, award=1))
    bulks.append(UserCoupon(type='bangka', user=user, award=2))
    bulks.append(UserCoupon(type='shoudan', user=user, award=5))
    UserCoupon.objects.bulk_create(bulks)
    sendmsg_bydhst(user.mobile, u"欢迎加入福利联盟大家庭，88元新手红包已发放，请查收。您的个人主页为：%s.51fanshu.com，快去分享给小伙伴吧！" % user.domain_name)
register_signal.connect(my_signal_handler, dispatch_uid="register")