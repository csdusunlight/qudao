#coding:utf-8
'''
Created on 2017年4月23日

@author: lch
'''
from account.transaction import charge_money
from wafuli_admin.models import UserStatis
from django.db.models import F
VIP_BONUS = {
    0:{'finance':0, 'task':0, 'money':0,},
    1:{'finance':0.01, 'task':0.10, 'money':500,},
    2:{'finance':0.02, 'task':0.15, 'money':3000,},
    3:{'finance':0.03, 'task':0.16, 'money':20000,},
    4:{'finance':0.04, 'task':0.18, 'money':80000,},
    5:{'finance':0.05, 'task':0.20, 'money':120000,},
}
VIP_AMOUNT = {0:0, 1:10000, 2:100000, 3:1000000, 4:5000000, 5:10000000,}
def get_vip_bonus(user, amount, type):
    if user.is_channel:
        return
    else:
        level = user.level
        cash = amount*VIP_BONUS[level][type]
        translist = charge_money(user, '0', cash, u'vip奖励')
def vip_judge(user, with_amount):
    obj, created = UserStatis.objects.get_or_create(user=user)
    obj.week_statis = F('week_statis') + with_amount
    obj.month_statis = F('month_statis') + with_amount
    obj.save(update_fields=['week_statis', 'month_statis'])
    if user.is_channel:
        return
    level = user.level
    total = user.with_total
    ntotal = user.with_total + with_amount
    user.with_total = ntotal
    keys = sorted(VIP_AMOUNT.keys())
    for key in keys:
        value = VIP_AMOUNT[key]
        if ntotal >= value and total < value:
            if key > level:
                user.level = key
                charge_money(user, '0', VIP_BONUS[key]['money'], u'VIP升级奖励')
                msg_content = u'恭喜您的会员等级提升为VIP' + str(key) + u'！'
    user.save(update_fields=['level', 'with_total'])
    