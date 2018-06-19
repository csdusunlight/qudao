#coding:utf-8
from django.shortcuts import render
from django.db import transaction, connection
from django.contrib.auth.decorators import login_required
from wafuli.models import InvestLog, Project
import datetime
from django.http.response import JsonResponse, HttpResponse
from decimal import Decimal
import logging
from merchant.margin_transaction import charge_margin
from public.permissions import CsrfExemptSessionAuthentication, IsOwnerOrStaff
from rest_framework import permissions, generics
from merchant.serializers import ApplyProjectSerializer, TranslogSerializer,\
    MarginAuditLogSerializer, MerchantProjectStatisticsSerializer
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog,\
    MerchantProjectStatistics, ZhifubaoTransaction
import django_filters
from rest_framework.filters import SearchFilter, OrderingFilter
from public.Paginations import MyPageNumberPagination
from merchant.Filters import ApplyProjectFilter, TranslogFilter,\
    MarginAuditLogFilter
from django.views.decorators.csrf import csrf_exempt
from account.transaction import charge_money
from django.db.models.aggregates import Count, Sum
from restapi.Filters import InvestLogFilter
from restapi.serializers import InvestLogSerializer
from collections import OrderedDict
from docs.models import DocStatis
from django.core.cache import cache
from public.tools import login_required_ajax, has_permission,\
    has_post_permission, random_code
from xlwt.Workbook import Workbook
from xlwt.Style import easyxf
import StringIO
import xlrd
import traceback
import json
from dragon import settings
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
        unaudited_num = InvestLog.objects.filter(project__user=admin_user, category='merchant', 
                                                 preaudit_state='1', audit_state='1').count() or ''
        except_num = InvestLog.objects.filter(project__user=admin_user, category='merchant', audit_state='3').count() or ''
        appeal_num = InvestLog.objects.filter(project__user=admin_user, category='merchant', audit_state='4').count() or ''
        return render(request,"preaudit_investlog.html", {'unaudited_pronames':unaudited_pronames,
                    'except_num':except_num, 'appeal_num':appeal_num, 'unaudited_num':unaudited_num})
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
                res['res_msg'] = u"操作失败，结算重复！"
            else:
                broker_rate = investlog.get_project_broker()
                broker_amount = cash * broker_rate/100
                if cash + broker_amount > admin_user.margin_account:
                    res['code'] = 1
                    res['res_msg'] = u"资金账户余额不足，请先存入足够金额！"
                    return JsonResponse(res)
                translist = charge_margin(admin_user, '1', cash, project_title)
                investlog.presettle_amount = cash
                investlog.broker_amount = broker_amount
                investlog.preaudit_state = '0'
                #对于异常数据，要改成未处理
                investlog.audit_state = '1'
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
            broker_rate = investlog.get_project_broker()
            broker_amount = delta * broker_rate/100
            if delta + broker_amount > admin_user.margin_account:
                res['code'] = 1
                res['res_msg'] = u"资金账户余额不足，请先存入足够金额！"
                return JsonResponse(res)
            translog = charge_margin(admin_user, '1', delta, project_title + u"补差价")
            translog.auditlog = investlog
            translog.save()
            broker_rate = investlog.project.broker_rate
            investlog.broker_amount = broker_amount
            if broker_amount > 0:
                translog2 = charge_margin(admin_user, '1', broker_amount, "佣金")
                translog2.auditlog = investlog
                translog2.save()
            translist = charge_money(investlog_user, '0', delta, project_title + u"补差价", auditlog=investlog)
            investlog.settle_amount = cash
            investlog.presettle_amount = cash
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
            doc_id = project.apply_project.strategy_id if hasattr(project, 'apply_project') else None
            if not doc_id:
                continue
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
        doc_id = project.apply_project.strategy_id if hasattr(project, 'apply_project') else None
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
        key = item['day']
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
    
@login_required
def export_merchant_investlog(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects.filter(category='merchant', project__user=user)
    investtime_0 = request.GET.get("investtime_0", None)
    investtime_1 = request.GET.get("investtime_1", None)
    submittime_0 = request.GET.get("submittime_0", None)
    submittime_1 = request.GET.get("submittime_1", None)
    auditdate_0 = request.GET.get("auditdate_0", None)
    auditdate_1 = request.GET.get("auditdate_1", None)
    state = request.GET.get("audit_state", None)
    preaudit_state = request.GET.get("preaudit_state", None)
    submit_type = request.GET.get('submit_type', '0')
    if investtime_0 and investtime_1:
        s = datetime.datetime.strptime(investtime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(investtime_1,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    if submittime_0 and submittime_1:
        s = datetime.datetime.strptime(submittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(submittime_1,'%Y-%m-%d')
        item_list = item_list.filter(submit_time__range=(s,e))
    if auditdate_0 and auditdate_1:
        s = datetime.datetime.strptime(auditdate_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(auditdate_1,'%Y-%m-%d')
        e += datetime.timedelta(days=1)
        item_list = item_list.filter(audit_time__range=(s,e))
#     qq_number = request.GET.get("qq_number", None)
#     if qq_number:
#         item_list = item_list.filter(user__qq_number=qq_number)
    mobile = request.GET.get("user_mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
    userlevel = request.GET.get("level",None)
    if userlevel:
        item_list = item_list.filter(user__level=userlevel)
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(project__company__name__contains=companyname)
    invest_mobile = request.GET.get("invest_mobile", None)
    if invest_mobile:
        item_list = item_list.filter(invest_mobile=invest_mobile)
    projectname = request.GET.get("project_title_contains", None)
    if projectname:
        item_list = item_list.filter(project__title__contains=projectname)
    if state:
        item_list = item_list.filter(audit_state=state).select_related('user', 'project').order_by('submit_time')
    if preaudit_state:
        item_list = item_list.filter(preaudit_state=preaudit_state).select_related('user', 'project').order_by('submit_time')
    data = []
    for con in item_list:
        project = con.project
        project_name=project.title
        invest_mobile=con.invest_mobile
        invest_name=con.invest_name
        invest_date=con.invest_date
        id=con.id
        remark= con.remark
        invest_amount= con.invest_amount
        term=con.invest_term
        qq_number = con.user.qq_number + '/' +  con.user.qq_name
        user_level = con.user.level
        result = ''
        settle_amount = ''
        settle_price = con.get_project_price()
        reason = con.audit_reason
        submit_type = con.get_submit_type_display()
        if con.preaudit_state=='0':
            result = u'通过'
            settle_amount = str(con.presettle_amount)
        elif con.preaudit_state=='2':
            result = u'拒绝'
        elif con.preaudit_state=='3':
            result = u'异常'
        data.append([id, project_name, invest_date, invest_mobile, invest_name, term,
                     invest_amount, settle_price,remark, result, settle_amount, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'投资日期', u'投资手机号', u'投资姓名' ,u'投资期限' ,u'投资金额', u'结算价格', u'备注',
                 u'审核结果(通过/拒绝/异常)',u'结算金额',u'审核说明']
    for i in range(len(title_row)):
        ws.write(0,i,title_row[i])
    row = len(data)
    style1 = easyxf(num_format_str='YY/MM/DD')
    for i in range(row):
        lis = data[i]
        col = len(lis)
        for j in range(col):
            if j==2:
                ws.write(i+1,j,lis[j],style1)
            else:
                ws.write(i+1,j,lis[j])
    sio = StringIO.StringIO()
    w.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=投资数据表.xls'
    response.write(sio.getvalue())
    return response

@csrf_exempt
@has_post_permission('100')
def import_merchant_investlog(request):
    admin_user = request.user
    ret = {'code':-1}
    file = request.FILES.get('file')
#     print file.name
    try:
        with open('./out.xls', 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        data = xlrd.open_workbook('out.xls')
        table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols
        if ncols!=12:
            ret['msg'] = u"文件格式与模板不符，请在导出的待审核记录表中更新后将文件导入！"
            return JsonResponse(ret)
        rtable = []
        mobile_list = []
        for i in range(1,nrows):
            temp = []
            duplic = False
            for j in range(ncols):
                cell = table.cell(i,j)
                if j==0:
                    id = int(cell.value)
                    temp.append(id)
                elif j==1:
                    project = cell.value
                    temp.append(project)
                elif j==9:
                    result = cell.value.strip()
                    if result == u"通过":
                        result = 1
                    elif result == u"拒绝":
                        result = 2
                    elif result == u"异常":
                        result = 3
                    else:
                        raise Exception(u"审核结果必须为通过,拒绝或异常。")
                    temp.append(result)
                elif j==10:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    elif result==1:
                        raise Exception(u"审核结果为通过时，结算金额不能为空或零。")
                    temp.append(return_amount)
                elif j==11:
                    reason = cell.value
                    temp.append(reason)
                    if result!=1 and not reason:
                        raise Exception(u"拒绝或异常数据要注明原因。")
                else:
                    continue;
            rtable.append(temp)
    except Exception, e:
        traceback.print_exc()
        ret['msg'] = unicode(e)
        ret['num'] = 0
        return JsonResponse(ret)
    admin_user = request.user
    suc_num = 0
    not_exist_list = []
    had_audited_list = []
    try:
        for row in rtable:
            with transaction.atomic():
                id = row[0]
                project_title=row[1]
                result = row[2]
                cash = row[3]
                reason = row[4]
                try:
                    investlog = InvestLog.objects.get(id=id)
                except InvestLog.DoesNotExist:
                    not_exist_list.append(id)
                    continue
                if not investlog.preaudit_state in ['1','3'] or not \
                    investlog.audit_state in ['1','3'] or investlog.translist.exists():
                    had_audited_list.append(id)
                    continue
                investlog_user = investlog.user
                translist = None
                if result==1:
                    broker_rate = investlog.get_project_broker()
                    broker_amount = cash * broker_rate/100
                    if cash + broker_amount > admin_user.margin_account:
                        raise Exception(u"资金余额不足，请先存入。") 
                    translist = charge_margin(admin_user, '1', cash, project_title)
                    investlog.presettle_amount = cash
                    investlog.broker_amount = broker_amount
                    investlog.preaudit_state = '0'
                    #对于异常数据，要改成未处理
                    investlog.audit_state = '1'
                    translist.auditlog = investlog
                    translist.save(update_fields=['content_type', 'object_id'])
                    if broker_amount > 0:
                        translist2 = charge_margin(admin_user, '1', broker_amount, "佣金")
                        translist2.auditlog = investlog
                        translist2.save(update_fields=['content_type', 'object_id'])
#                     #活动插入
#                     on_audit_pass(request, investlog)
#                     #活动插入结束
                elif result==2:
                    investlog.preaudit_state = '2'
                    investlog.audit_state = '2'
                elif result==3:
                    investlog.preaudit_state = '3'
                    investlog.audit_state = '3'
                investlog.audit_reason = reason    
                investlog.preaudit_time = datetime.datetime.now()
                investlog.admin_user = admin_user
                investlog.save()
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    ret['not_exist_list'] = not_exist_list
    ret['had_audited_list'] = had_audited_list
    return JsonResponse(ret)

@csrf_exempt
def transfer_callback(request):
    info = json.loads(request.body)
    if info['secret'] != settings.CALLBACK_TOKEN:
        return JsonResponse({'code':-1})
    for item in info['content']:
        time = item['time']
        time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        tradeNo = item['tradeNo']
        amount = Decimal(item['amount'])
        remark = item['remark']
        print item
        try:
            trans = ZhifubaoTransaction.objects.get(remark=remark, amount=amount, transNo='')
            print trans
        except ZhifubaoTransaction.DoesNotExist:
            continue
        else:
            with transaction.atomic():
                trans.transNo = tradeNo
                trans.time = time
                trans.save()
                charge_margin(trans.user, '0', amount, u"充值")
    return JsonResponse({'code':0})

@csrf_exempt
@has_permission('100')
def create_zhifubao_transaction(request):
    amount = request.POST.get('amount')
    amount = Decimal(amount)
    trans = None
    remark = ''
    msg = ''
    for i in range(5):
        try:
            remark = random_code()
            trans = ZhifubaoTransaction.objects.create(remark=remark, amount=amount, user=request.user)
        except Exception as e:
            msg = str(e)
            continue
        else:
            break
    if trans:
        code = 0
        msg = 'ok'
    else:
        code = 1
        remark = ''
    return JsonResponse({'code':code, 'remark':remark, 'msg':msg})

@csrf_exempt
def merchant_guide(request): #jzy
    return render(request, 'merchant_guide.html')