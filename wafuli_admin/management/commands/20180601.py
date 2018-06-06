
#coding:utf-8
'''
Created on 2017年4月12日

@author: lch
'''
from django.core.management.base import BaseCommand
from coupon.models import UserCoupon
from wafuli.models import Project
from account.varify import sendmsg_bydhst, send_multimsg_bydhst
from account.models import MyUser
class Command(BaseCommand):
    def handle(self, *args, **options):
#         send_multimsg_bydhst('18500581509,15084809280', u"活动上线测试短信")
        a = MyUser.objects.all().values('mobile')
        phone_list = [x['mobile'] for x in a[0:500]]
        phone_list2 = [x['mobile'] for x in a[500:]]
        phones1 = ','.join(phone_list)
        phones2 = ','.join(phone_list2)
        content = u'6.1儿童节，宝宝们节日快乐，福利联盟送您188现金大红包啦！快去【福利联盟官微】领取吧，http://t.cn/R19unV8，退订TD'
        send_multimsg_bydhst(phones1, content)
        send_multimsg_bydhst(phones2, content)
        

            
