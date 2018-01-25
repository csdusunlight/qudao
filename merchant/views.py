#coding:utf-8
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from wafuli.models import InvestLog, Project
import datetime
from django.http.response import JsonResponse
from decimal import Decimal
import logging
from merchant.margin_transaction import charge_margin
from public.permissions import CsrfExemptSessionAuthentication, IsOwnerOrStaff
from rest_framework import permissions, generics
from merchant.serializers import ApplyProjectSerializer, TranslogSerializer,\
    MarginAuditLogSerializer
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog
import django_filters
from rest_framework.filters import SearchFilter
from public.Paginations import MyPageNumberPagination
from merchant.Filters import ApplyProjectFilter, TranslogFilter,\
    MarginAuditLogFilter
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger('wafuli')
# Create your views here.
@csrf_exempt
@transaction.atomic
def preaudit_investlog(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('merchant:preaudit_investlog'))
        item_list = InvestLog.objects.filter(user=admin_user, category='merchant', audit_state__in=['1','3'], submit_time__lt=datetime.date.today()).values_list('project_id').distinct().order_by('project_id')
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
        if not investlog_id or type==1 and not cash or not type in [1, 2, 3]:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        investlog = InvestLog.objects.get(id=investlog_id)
        investlog_user = investlog.user
        card = investlog_user.user_bankcard.first()

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
            if not investlog.audit_state in ['1', '3']:
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if not investlog.preaudit_state in ['1','3']:
                res['code'] = -3
                res['res_msg'] = u'该项目已预审核过，不要重复审核！'
                return JsonResponse(res)
            if investlog.audit_state == '1' and investlog.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -5
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                investlog.preaudit_state = '0'
                translist = charge_margin(investlog_user, '1', cash, project_title)
                investlog.presettle_amount = cash
                broker_rate = investlog.project.broker_rate
                broker_amount = cash * broker_rate/100
                investlog.broker_amount = broker_amount
                if broker_amount > 0:
                    translist2 = charge_margin(investlog_user, '1', broker_amount, "佣金")
                translist.auditlog = investlog
                translist2.auditlog = investlog
                translist.save()
                translist2.save()
#                 #活动插入
#                 on_audit_pass(request, investlog)
#                 #活动插入结束
                res['code'] = 0
        elif type==2:
            investlog.preaudit_state = '2'
            res['code'] = 0
        elif type==3:
            investlog.preaudit_state = '3'
            investlog.audit_state = '3'
            res['code'] = 0
        investlog.audit_reason = reason
        if res['code'] == 0:
            investlog.preaudit_time = datetime.datetime.now()
            investlog.save()
        return JsonResponse(res)
    
@csrf_exempt
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

def bail_manage(request):
    return render(request, 'bail_manage.html')
def proj_manage(request):
    return render(request, 'proj_manage.html')    
def proj_add(request):
    return render(request, 'proj_add.html')
def fangdan_audit(request):
    return render(request, 'fangdan_audited.html')
    
@csrf_exempt
@login_required
def merchant(request):
    user = request.user
    if request.method == 'GET':
        card = user.user_bankcard.first()
        return render(request,'merchant_index.html',)
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
