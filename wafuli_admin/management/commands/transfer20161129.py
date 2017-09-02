
#coding:utf-8
'''
Created on 2016年8月13日

@author: lch
'''
import logging
from wafuli.models import UserEvent, ZeroPrice, Hongbao, Welfare, Baoyou, Task,\
    Finance, TransList
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
from wafuli_admin.models import RecommendRank, DayStatis
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
#         free_wels = Welfare.objects.all()
#         tasks = Task.objects.all()
#         finance = Finance.objects.all()
#         wels = list(free_wels)+list(tasks)+list(finance)
#         for wel in wels:
#             wel.seo_title = wel.seo_title + u" - 挖福利"
#             wel.save(update_fields=['seo_title']);
#         wels = Welfare.objects.update(startTime=F('pub_date'))
#         baoyou = Baoyou.objects.all()
#         for wel in baoyou:
#             wel.url = reverse('exp_welfare_openwindow') + '?id=' + str(wel.id)+ "&type=Welfare"
#             wel.save()
#         zero_all = ZeroPrice.objects.all()
#         for zero in zero_all:
#             wel = Hongbao.objects.create(title=zero.title,news_priority=zero.news_priority,
#                                          pub_date=zero.pub_date,view_count=zero.view_count,change_user=zero.change_user,
#                                          state=zero.state,pic=zero.pic,isonMobile=zero.isonMobile,exp_url=zero.exp_url,
#                                          exp_code=zero.exp_code,advert=zero.advert,company=zero.company,
#                                          seo_title=zero.seo_title,seo_keywords=zero.seo_keywords,
#                                          seo_description=zero.seo_description,provider=zero.provider,
#                                          time_limit=zero.time_limit,type='hongbao',strategy=zero.strategy)
#         wei_list = Welfare.objects.all()
#         for obj in wei_list:
#             obj.url = reverse('welfare', kwargs={'id': obj.pk})
#             obj.save(update_fields=['url',])
        print 'users'
        users = MyUser.objects.all()
        for user in users:
            user.balance = 100*F('balance')
            user.accu_income = 100*F('accu_income')
            user.invite_income = 100*F('invite_income')
            user.invite_account = 100*F('invite_account')
            user.save()
        print 'trans'
        trans = TransList.objects.all()
        for tran in trans:
            tran.initAmount = 100*F('initAmount')
            tran.transAmount = 100*F('transAmount')
            tran.save()
        print 'daystati'
        trans = DayStatis.objects.all()
        for tran in trans:
            tran.with_amount = 100*F('with_amount')
            tran.ret_amount = 100*F('ret_amount')
            tran.coupon_amount = 100*F('coupon_amount')
            tran.save()
        print 'rank'
        trans = RecommendRank.objects.all()
        for tran in trans:
            tran.award = 100*F('award')
            tran.save()
        print 'task'
        trans = Task.objects.all()
        for tran in trans:
            tran.moneyToAdd = 100*F('moneyToAdd')
            tran.state = '3'
            tran.save()
        print 'event'
        events = UserEvent.objects.filter(event_type__in=['2','5'])
        for event in events:
            event.invest_amount = 100*F('invest_amount')
            event.save(update_fields=['invest_amount'])