#coding:utf-8
from django.shortcuts import render, redirect
from django.db import transaction, connection
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from wafuli.models import InvestLog, Project
import datetime
from django.http.response import JsonResponse
from decimal import Decimal
import logging
from merchant.margin_transaction import charge_margin, ChargeValueError
from public.permissions import CsrfExemptSessionAuthentication, IsOwnerOrStaff
from rest_framework import permissions, generics
from merchant.serializers import ApplyProjectSerializer, TranslogSerializer,\
    MarginAuditLogSerializer, MerchantProjectStatisticsSerializer
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog,\
    MerchantProjectStatistics
import django_filters
from rest_framework.filters import SearchFilter, OrderingFilter
from public.Paginations import MyPageNumberPagination
from merchant.Filters import ApplyProjectFilter, TranslogFilter,\
    MarginAuditLogFilter
from django.views.decorators.csrf import csrf_exempt
from account.transaction import charge_money
from django.db.models.aggregates import Count, Sum
from dircache import annotate
from restapi.Filters import InvestLogFilter
from restapi.serializers import InvestLogSerializer
from collections import OrderedDict
from docs.models import DocStatis
from django.core.cache import cache
from public.tools import login_required_ajax, has_permission
logger = logging.getLogger('wafuli')
# Create your views here.
@csrf_exempt
@login_required
@transaction.atomic
@has_permission('100')
def preaudit_investlog(request):
    admin_user = request.user
    if request.method == "GET":
        item_list = InvestLog.objects.filter(project__user=admin_user, category='merchant', audit_state__in=['1','3'], submit_time__lt=datetime.date.today()).values_list('project_id').distinct().order_by('project_id')
        project_list = ()
        for item in item_list:
            project_list += item
        projects = Project.objects.filter(id__in=project_list)
        unaudited_pronames = []
        for project in projects:
            unaudited_pronames.append(project.title)
        return render(request,"preaudit_investlog.html", {'unaudited_pronames':unaudited_pronames})
    if request.method == "POST":
        res = {}
        investlog_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', '')
        type = int(type)
        if not reason and type in [ 2, 3, 5 ]:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足！'
            return JsonResponse(res)
        investlog = InvestLog.objects.get(id=investlog_id)
        investlog_user = investlog.user

        project = investlog.project
        project_title = project.title

        translist = None
        if type==1:
            try:
                cash = Decimal(cash)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if not investlog.audit_state in ['1', '3', '4']:
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if not investlog.preaudit_state in ['1','3','4']:
                res['code'] = -3
                res['res_msg'] = u'该项目已预审核过，不要重复审核！'
                return JsonResponse(res)
            if investlog.audit_state == '1' and investlog.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -5
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                broker_rate = investlog.project.broker_rate
                broker_amount = cash * broker_rate/100
                if cash + broker_amount > admin_user.margin_account:
                    res['code'] = 1
                    res['res_msg'] = u"资金账户余额不足，请先存入足够金额！"
                    return JsonResponse(res)
                translist = charge_margin(admin_user, '1', cash, project_title)
                investlog.presettle_amount = cash
                investlog.broker_amount = broker_amount
                investlog.preaudit_state = '0'
                translist.auditlog = investlog
                translist.save(update_fields=['content_type', 'object_id'])
                if broker_amount > 0:
                    translist2 = charge_margin(admin_user, '1', broker_amount, "佣金")
                    translist2.auditlog = investlog
                    translist2.save(update_fields=['content_type', 'object_id'])
#                 #活动插入
#                 on_audit_pass(request, investlog)
#                 #活动插入结束
                res['code'] = 0
        elif type==2:
            investlog.preaudit_state = '2'
            investlog.audit_state = '2'
            res['code'] = 0
        elif type==3:
            investlog.preaudit_state = '3'
            investlog.audit_state = '3'
            res['code'] = 0
        #申诉数据处理，4：接受申诉 5：拒绝申诉
        elif type==4:
            investlog.audit_state = '0'
            try:
                cash = Decimal(cash)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash <= investlog.settle_amount:
                res['code'] = -3
                res['res_msg'] = u"申诉数据修正金额必须大于原结算金额！"
                return JsonResponse(res)
            delta = cash - investlog.settle_amount
            broker_amount = delta * broker_rate/100
            if delta + broker_amount > admin_user.margin_account:
                res['code'] = 1
                res['res_msg'] = u"资金账户余额不足，请先存入足够金额！"
                return JsonResponse(res)
            translog = charge_margin(admin_user, '1', delta, project_title + u"补差价")
            broker_rate = investlog.project.broker_rate
            investlog.broker_amount = broker_amount
            if broker_amount > 0:
                translog2 = charge_margin(admin_user, '1', broker_amount, "佣金")
            translog.auditlog = investlog
            translog2.auditlog = investlog
            translog.save()
            translog2.save()
            translist = charge_money(investlog_user, '0', delta, project_title + u"补差价")
            investlog.settle_amount = cash
            translist.auditlog = investlog
            translist.save(update_fields=['content_type', 'object_id'])
            res['code'] = 0
        elif type==5:
            if investlog.settle_amount > 0:
                investlog.audit_state = '0'
            else:
                investlog.audit_state = '2'
            res['code'] = 0
        if res['code'] == 0:
            investlog.audit_reason = reason
            investlog.preaudit_time = datetime.datetime.now()
            investlog.audit_time = datetime.datetime.now()
            investlog.save()
        return JsonResponse(res)
    
@csrf_exempt
@has_permission('100')
def stop_project(request):
    res = {}
    id = request.POST.get('id')
    id = int(id)
    apply_project = Apply_Project.objects.get(id=id, user=request.user)
    doc = apply_project.strategy
    project = apply_project.project
    if not project or project.state!='10':
        res['code'] = 1
        res['msg'] = u"非进行中项目，不可停止"
    assert(project.user==request.user)
    project.state = '20'
    doc.is_on = False
    project.save(update_fields=['state'])
    doc.save(update_fields=['is_on'])
    res['code'] = 0
    return JsonResponse(res)

@login_required
@has_permission('100')
def proj_manage(request):
    return render(request, 'proj_manage.html')  
@login_required
@has_permission('100')  
def proj_add(request):
    return render(request, 'proj_add.html')
@login_required
@has_permission('100')
def fangdan_audit(request):
    return render(request, 'fangdan_audited.html')
    
@csrf_exempt
@login_required
@has_permission('100')
def merchant(request):
    user = request.user
    if request.method == 'GET':
        today = datetime.date.today()
        online_count = Project.objects.filter(user=user, category="merchant", state__in=['10','20']).count()
        total_toaudit_count = InvestLog.objects.filter(project__user=user, category="merchant", audit_state='1',
                                preaudit_state='1').count()
        total_pv = 0
        total_settle_amount = 0
        total_submit_count = 0
        total_settle_count = 0
        projects = Project.objects.filter(user=user, category="merchant", state__in=['10','20']).\
            only('id', 'state', 'apply_project__strategy_id').order_by('state','-pub_date')
        for project in projects:
            doc_id = project.apply_project.strategy_id
            pv = 0
            try:
                pv = DocStatis.objects.get(doc_id=doc_id, date=today).count
            except:
                pass
            cache_value = cache.get('doc_%s' % doc_id)
            if cache_value:
                pv += cache_value
            total_pv += pv
        total_submit_count = InvestLog.objects.filter(project__user=user, category="merchant", submit_time__gte=today).count()
        settle_data = InvestLog.objects.filter(project__user=user, category="merchant",
                audit_time__gte=today, audit_state='0').aggregate(sumofsettle=Sum('settle_amount'),count=Count('*'))
        total_settle_amount = settle_data['sumofsettle'] or 0
        total_settle_count = settle_data['count'] or 0
        today_data = {'online_count':online_count, 
                      'total_pv':total_pv,
                      'total_toaudit_count':total_toaudit_count,
                      'total_submit_count':total_submit_count,
                      'total_settle_count':total_settle_count,
                      'total_settle_amount':total_settle_amount,
                      }
        return render(request,'merchant_index.html',today_data)
    elif request.method == 'POST':
        result = {'code':-1, 'res_msg':''}
        amount = request.POST.get("amount", None)
        type = request.POST.get("type", None)
        if not amount or not type:
            result['code'] = 3
            result['res_msg'] = u'传入参数不足！'
            return JsonResponse(result)
        try:
            amount = Decimal(amount)
            assert(type in ['0', '1'] and amount > 0)
        except ValueError:
            result['code'] = -1
            result['res_msg'] = u'参数不合法！'
            return JsonResponse(result)
        if type == 1 and ( amount < 10 or amount > user.margin_account ):
            result['code'] = -1
            result['res_msg'] = u'提现金额错误！'
            return JsonResponse(result)
        card = user.user_bankcard.first()
        if type==1 and not card:
            result['code'] = -1
            result['res_msg'] = u'请先绑定银行卡！'
            return JsonResponse(result)
        try:
            with transaction.atomic():
                translist = charge_margin(user, '1', amount, u'提现')
                event = Margin_AuditLog.objects.create(user=user, amount=amount, audit_state='1', type=type)
                translist.auditlog = event
                translist.save()
                result['code'] = 0
        except:
            result['code'] = -2
            result['res_msg'] = u'提现失败！'
        return JsonResponse(result)

@csrf_exempt
@login_required
@has_permission('100')
def merchant_detail_proj(request):
    return render(request,'merchant_detail_proj.html',{})

@csrf_exempt
@login_required
@has_permission('100')
def merchant_detail_day(request):
    return render(request,'merchant_detail_day.html',{})

@login_required_ajax
@has_permission('100')
def get_project_statis_byday(request):
    user = request.user
    _range = request.GET.get('range', 0)
    _range = int(_range)
#     if cache.has_key('user_%s_merchant_project_statistic' % user.id):
#         params = cache.get('user_%s_merchant_project_statistic' % user.id)
#     else:
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    sevendaysago = today - datetime.timedelta(days=6)
    thirtydaysago = today - datetime.timedelta(days=29)
    projects = Project.objects.filter(user=user, category="merchant").\
        only('id', 'state', 'apply_project__strategy_id').order_by('state','-pub_date')
    projects_statis_dict = OrderedDict()
    for project in projects:
        dic = {'title':project.title, 'submit_count':0, 'settle_amount':0, 'settle_count':0}
        doc_id = project.apply_project.strategy_id
        pv = 0
        if _range == 0:
            try:
                pv = DocStatis.objects.get(doc_id=doc_id, date=today).count
            except:
                pass
        elif _range == 1:
            pv = DocStatis.objects.filter(doc_id=doc_id, date=yesterday).aggregate(count=Sum('count'))['count'] or 0
        elif _range == 7:
            pv = DocStatis.objects.filter(doc_id=doc_id, date__gte=sevendaysago).aggregate(count=Sum('count'))['count'] or 0
        else:
            pv = DocStatis.objects.filter(doc_id=doc_id, date__gte=thirtydaysago).aggregate(count=Sum('count'))['count'] or 0
        cache_value = cache.get('doc_%s' % doc_id)
        if cache_value:
            pv += cache_value
        dic.update(pv=pv)
        projects_statis_dict[project.id] = dic
    
    list_submit = InvestLog.objects.filter(project__user=user, category="merchant")
    list_audite = InvestLog.objects.filter(project__user=user, category="merchant", audit_state='0')
    if _range == 0:
        list_submit = list_submit.filter(submit_time__gte=today)
        list_audite = list_audite.filter(audit_time__gte=today)
    elif _range == 1:
        list_submit = list_submit.filter(submit_time__range=[yesterday, today])
        list_audite = list_audite.filter(audit_time__range=[yesterday, today])
    elif _range == 7:
        list_submit = list_submit.filter(submit_time__gte=sevendaysago)
        list_audite = list_audite.filter(audit_time__gte=sevendaysago)
    else:
        list_submit = list_submit.filter(submit_time__gte=thirtydaysago)
        list_audite = list_audite.filter(audit_time__gte=thirtydaysago)
    list_submit = list_submit.values('project_id').annotate(count=Count('*')).order_by('project_id')
    list_audite = list_audite.values('project_id').annotate(sumofsettle=Sum('settle_amount'),
                count=Count('*')).order_by('project_id')
    for item in list_submit:
        id = item['project_id']
        if projects_statis_dict.has_key(id):
            projects_statis_dict[id].update(submit_count=item['count'])
    for item in list_audite:
        id = item['project_id']
        if projects_statis_dict.has_key(id):
            projects_statis_dict[id].update(settle_count=item['count'])
            projects_statis_dict[id].update(settle_amount=item['sumofsettle'])
    return JsonResponse(projects_statis_dict)

@login_required_ajax
@has_permission('100')
def get_days_statis(request):
    user = request.user
    _range = request.GET.get('range', 1)
    _range = int(_range)
    today = datetime.date.today()
    ndaysago = today - datetime.timedelta(days=_range-1)
    user = request.user
    select1 = {'day': connection.ops.date_trunc_sql('day', 'submit_time')}
    select2 = {'day': connection.ops.date_trunc_sql('day', 'audit_time')}
    dict_list = InvestLog.objects.filter(project__user=user, category="merchant", submit_time__gte=ndaysago).\
            extra(select=select1).values('day').annotate(count=Count('id')).order_by('-day')
    dict_list2 = InvestLog.objects.filter(project__user=user, category="merchant",
                audit_time__gte=ndaysago, audit_state='0').extra(select=select2).values('day').\
                annotate(count=Count('id'),sumofsettle=Sum('settle_amount')).order_by('-day')
    days_data = OrderedDict()
    for i in range(_range):
        day = today - datetime.timedelta(days=i)
        day = str(day)
        days_data[day]={
            'submit_count':0,
            'settle_count':0,
            'settle_amount':0,
        }
    for item in dict_list:
        key = item['day']
        if type(key) == datetime.datetime:
            key = datetime.datetime.strftime(item['day'],'%Y-%m-%d')
        days_data.get(key)['submit_count'] = item['count']
    for item in dict_list2:
        if type(key) == datetime.datetime:
            key = datetime.datetime.strftime(item['day'],'%Y-%m-%d')
        days_data.get(key)['settle_count'] = item['count']
        days_data.get(key)['settle_amount'] = item['sumofsettle']
    return JsonResponse(days_data)

@csrf_exempt
@login_required
@has_permission('100')
def margin_manage(request):
    user = request.user
    if request.method == 'GET':
        card = user.user_bankcard.first()
        return render(request,'margin_manage.html',)
    elif request.method == 'POST':
        result = {'code':-1, 'res_msg':''}
        amount = request.POST.get("amount", None)
        type = request.POST.get("type", None)
        if not amount or not type:
            result['code'] = 3
            result['res_msg'] = u'传入参数不足！'
            return JsonResponse(result)
        try:
            amount = Decimal(amount)
            assert(type in ['0', '1'] and amount > 0)
        except ValueError:
            result['code'] = -1
            result['res_msg'] = u'参数不合法！'
            return JsonResponse(result)
        if type == '1' and ( amount < 10 or amount > user.margin_account ):
            result['code'] = -1
            result['res_msg'] = u'提现金额错误！'
            return JsonResponse(result)
        card = user.user_bankcard.first()
        if type=='1':
            if not card:
                result['code'] = -1
                result['res_msg'] = u'请先绑定银行卡！'
                return JsonResponse(result)
            try:
                with transaction.atomic():
                    translist = charge_margin(user, '1', amount, u'提现')
                    event = Margin_AuditLog.objects.create(user=user, amount=amount, audit_state='1', type='1')
                    translist.auditlog = event
                    translist.save()
                    result['code'] = 0
            except:
                result['code'] = -2
                result['res_msg'] = u'提现失败！'
        elif type =='0':
            Margin_AuditLog.objects.create(user=user, amount=amount, audit_state='1', type='0')
            result['code'] = 0
        return JsonResponse(result)
    
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
class ApplyProjectList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Apply_Project.objects.all()
        else:
            return Apply_Project.objects.filter(user=user)
        
    serializer_class = ApplyProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend)
#     filter_fields = ['state','type','is_multisub_allowed','is_official']
    filter_class = ApplyProjectFilter
#     ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('title', )
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        print serializer.validated_data
        obj = serializer.save(user=self.request.user, audit_state='1')
class ApplyProjectDetail(BaseViewMixin, generics.RetrieveUpdateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Apply_Project.objects.all()
        else:
            return Apply_Project.objects.filter(user=user)
    serializer_class = ApplyProjectSerializer
    
class TranslogList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Margin_Translog.objects.all()
        else:
            return Margin_Translog.objects.filter(user=user)
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = TranslogSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = TranslogFilter

class MarginAuditLogList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Margin_AuditLog.objects.all()
        else:
            return Margin_AuditLog.objects.filter(user=user)
    serializer_class = MarginAuditLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = MarginAuditLogFilter
    pagination_class = MyPageNumberPagination

class InvestlogList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.filter(category='merchant')
        else:
            return InvestLog.objects.filter(category='merchant',project__user=user)
    serializer_class = InvestLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('submit_time',)
    filter_class = InvestLogFilter
    pagination_class = MyPageNumberPagination

class MerchantProjectStatisticsList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        return MerchantProjectStatistics.objects.filter(project__user=user, project__state__in=['10','20'])
    ordering_fields = ('project__doc__view_count',)
    serializer_class = MerchantProjectStatisticsSerializer
    filter_backends = (OrderingFilter,)
    pagination_class = MyPageNumberPagination