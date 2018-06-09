#coding:utf-8
'''
Created on 20160417

@author: zhlvch
'''

import logging
import time,datetime
# from django.db import connection
from django.db.models import Sum, Count,Avg,F
from wafuli.models import Project, WithdrawLog, InvestLog, TransList, AdminLog
# from activity.models import IPAward, IPLog
from docs.models import Document, DocStatis
from django.core.cache import cache
from public.redis import cache_decr_or_set
from merchant.models import MerchantProjectStatistics, Margin_AuditLog,\
    Margin_Translog
from coupon.models import UserCoupon
from django.contrib.contenttypes.models import ContentType
logger = logging.getLogger("wafuli")
from django.core.management.base import BaseCommand, CommandError
from account.models import MyUser, Userlogin, ApplyLogForChannel
from wafuli_admin.models import DayStatis, GlobalStatis
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Statistics is beginning*********")
        begin_time = time.time()
        today = datetime.date.today() 
        yesterday = today - datetime.timedelta(days=1)
        apply_num = ApplyLogForChannel.objects.filter(submit_time__gte=today).count()
        refuse_num = ApplyLogForChannel.objects.filter(audit_time__gte=today,audit_state='2').count()
        new_reg_num = MyUser.objects.filter(date_joined__gte=today).count()
        dict = WithdrawLog.objects.filter(audit_time__gte=today, audit_state='0').\
                aggregate(cou=Count('user_id',distinct=True),sum=Sum('amount'))
        with_amount = dict.get('sum') or 0
        with_num = dict.get('cou')
        ret = TransList.objects.filter(time__gte=today,transType='0').values('content_type').\
                annotate(sum=Sum('transAmount')).order_by('content_type')
        investtype = ContentType.objects.get_for_model(InvestLog).id
        admintype = ContentType.objects.get_for_model(AdminLog).id
        coupontype = ContentType.objects.get_for_model(UserCoupon).id
        ret_amount = 0
        admin_amount = 0
        coupon_amount = 0
        for item in ret:
            if item['content_type'] == investtype:
                ret_amount = item['sum']
            elif item['content_type'] == admintype:
                admin_amount = item['sum']
            elif item['content_type'] == coupontype:
                coupon_amount = item['sum']
#         ret_num = dict.get('cou')
        
        new_project_num = Project.objects.filter(pub_date__gte=today).count()
        ret = InvestLog.objects.filter(submit_time__gte=today).aggregate(sum=Sum('invest_amount'))
        invest_amount = ret.get('sum') or 0
#         dict = IPLog.objects.filter(time__gte=today).aggregate(total=Sum('award'))
#         activity_consume = dict.get('total')
        
        update_fields = {
                        'apply_num':apply_num,
                        'refuse_num':refuse_num,
                        'new_reg_num':new_reg_num,
                        'with_amount':with_amount,
                        'with_num':with_num,
                        'admin_amount':admin_amount,
                        'coupon_amount':coupon_amount,
                        'ret_amount':ret_amount,
                        'invest_amount':invest_amount,
#                         'ret_num':ret_num,
                        'new_project_num':new_project_num,
#                         'activity_consume':activity_consume
        }
        DayStatis.objects.update_or_create(date=today, defaults=update_fields)
        
        first_day = datetime.datetime(today.year, today.month, 1)
        
        with_total = MyUser.objects.aggregate(sum=Sum('accu_income'))
        invest_total = InvestLog.objects.filter(audit_state='0').aggregate(sum=Sum('invest_amount'),
                            count=Count('*'))
        global_statis = GlobalStatis.objects.first()
        if not global_statis:
            global_statis = GlobalStatis()
        global_statis.all_wel_num = Project.objects.count()
        global_statis.with_total = ((with_total.get('sum') or 0) + 91630000)/10000
        global_statis.invest_total = ((invest_total.get('sum') or 0) + 4836240000)/10000
        global_statis.user_total = MyUser.objects.count() + 300
        global_statis.invite_total = (invest_total.get('count') or 0) + 4180000
        global_statis.save()
        
        #文档定时关闭
        Document.objects.filter(close_time__lte=datetime.datetime.now(), is_on=True).update(is_on=False, close_time=None)
        
        #文档访问次数持久化
        keys_list = cache.keys('doc_*')
        kv_dict = cache.get_many(keys_list)
        for k,v in kv_dict.items():
            if v > 0:
                id = k[4:]
                doc = Document.objects.filter(id=id).first()
                if doc:
                    obj, created = DocStatis.objects.get_or_create(date=today, doc_id=id)
                    doc.view_count = F('view_count')+v
                    obj.count = F('count')+v
                    obj.save(update_fields=['count',])
                    doc.save(update_fields=['view_count'])
                    cache_decr_or_set(k, v)
                    cache.expire(k, 24*60*60)
                else:
                    cache.delete(k)
         
         
        #统计放单项目数据
        ret = InvestLog.objects.filter(category='merchant', project__state__in=['10', '20']).values('project_id',
                                'audit_state').annotate(count=Count('*'), sum=Sum('settle_amount')).order_by(
                                'project_id','audit_state')
        project_statis = {}
        view_count = 0
        settle_count = 0
        appeal_count = 0
        abnormal_count = 0
        toaudit_count = 0
        settle_amount = 0
        for item in ret:
            id = item['project_id'] 
            if id not in project_statis:
                project_statis[id]={
                    'settle_count' : 0,
                    'settle_amount' :0,
                    'toaudit_count' :0,
                    'appeal_count' :0,
                    'abnormal_count':0,
                    'submit_count':0,
                }
            project_statis[id]['submit_count'] += item['count']
            if item['audit_state'] == '0':
                project_statis[id]['settle_count'] = item['count']
                project_statis[id]['settle_amount'] = item['sum']
            elif item['audit_state'] == '1':
                project_statis[id]['toaudit_count'] += item['count']
            elif item['audit_state'] == '2':
                project_statis[id]['toaudit_count'] = item['count']
            elif item['audit_state'] == '3':
                project_statis[id]['abnormal_count'] = item['count']
                project_statis[id]['toaudit_count'] += item['count']
            elif item['audit_state'] == '4':
                project_statis[id]['appeal_count'] = item['count']
                project_statis[id]['toaudit_count'] += item['count']
        for k,v in project_statis.items():
            MerchantProjectStatistics.objects.update_or_create(project_id=k, defaults=v)
        
        #放单数据每日统计For Admin
        merchant_people = MyUser.objects.filter(admin_permissions__code='100', is_staff=False).count()
        dic = Project.objects.filter(category='merchant', state='10').aggregate(user_count=Count('user_id', distinct=True),
                count = Count('*'))
        merchant_people_active = dic.get('user_count') or 0
        merchant_projects = dic.get('count') or 0
        
        merchant_investlogs_submit = InvestLog.objects.filter(category='merchant', submit_time__gte=today).count()
        dic = InvestLog.objects.filter(category='merchant', audit_state='0', audit_time__gte=today).aggregate(
                broker_amount=Sum('broker_amount'), settle_amount=Sum('settle_amount'), count = Count('*'))
        merchant_broker = dic.get('broker_amount') or 0
        merchant_settle = dic.get('settle_amount') or 0
        merchant_investlogs_audit = dic.get('amount') or 0
        merchant_consume = merchant_settle + merchant_broker
        dic = Margin_Translog.objects.filter(reason__contains=u"充值",transType='0',time__gte=today).aggregate(merchant_charge=Sum('transAmount'))
        merchant_charge = dic.get('merchant_charge') or 0
        update_fields = {
            'merchant_people': merchant_people,
            'merchant_people_active': merchant_people_active,
            'merchant_projects': merchant_projects,
            'merchant_investlogs_submit':merchant_investlogs_submit,
            'merchant_investlogs_audit':merchant_investlogs_audit,
            'merchant_charge': merchant_charge,
            'merchant_consume': merchant_consume,
            'merchant_broker': merchant_broker,
            'merchant_settle': merchant_settle
        }
        DayStatis.objects.filter(date=today).update(**update_fields)
        
        dic = UserCoupon.objects.filter(create_date=today).aggregate(count_user=Count('user', distinct=True),
                    count_coupon=Count('*'), sum=Sum('award'))
        coupon_user_total = dic.get('count_user') or 0
        coupon_total = dic.get('count_coupon') or 0
        coupon_award = dic.get('sum') or 0
        dic = UserCoupon.objects.filter(unlock_date=today).aggregate(count_user=Count('user', distinct=True),
                    count_coupon=Count('*'), sum=Sum('award'))
        coupon_user_total_unlock = dic.get('count_user') or 0
        coupon_total_unlock = dic.get('count_coupon') or 0
        coupon_award_unlock = dic.get('sum') or 0
        update_fields = {
            'coupon_user_total': coupon_user_total,
            'coupon_total': coupon_total,
            'coupon_award': coupon_award,
            'coupon_user_total_unlock':coupon_user_total_unlock,
            'coupon_total_unlock':coupon_total_unlock,
            'coupon_award_unlock': coupon_award_unlock,
        }
        DayStatis.objects.filter(date=today).update(**update_fields)
        
        end_time = time.time()
        logger.info("******Statistics is finished, time:%s*********",end_time-begin_time)
