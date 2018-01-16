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
logger = logging.getLogger('wafuli')
# Create your views here.
@transaction.atomic
def preaudit_investlog(request):
    admin_user = request.user
    if request.method == "GET":
        print reverse('merchant:preaudit_investlog')
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
            if investlog.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                translist = charge_margin(investlog_user, '0', cash, project_title)
                investlog.audit_state = '0'
                investlog.settle_amount = cash
                translist.investlog = investlog
                translist.save(update_fields=['investlog'])
#                 #活动插入
#                 on_audit_pass(request, investlog)
#                 #活动插入结束
                res['code'] = 0
        elif type==2:
            investlog.audit_state = '2'
            res['code'] = 0
        elif type==3:
            investlog.audit_state = '3'
            res['code'] = 0
        investlog.audit_reason = reason
        if res['code'] == 0:
            investlog.audit_time = datetime.datetime.now()
            investlog.admin_user = admin_user
            investlog.save()
        return JsonResponse(res)
    
    def fangdan_audit(request):
        return render(request, 'merchant/fangdan_audited.html')