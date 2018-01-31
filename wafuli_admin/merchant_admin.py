#coding:utf-8
'''
Created on 2018年1月17日

@author: lch
'''
from django.db import transaction
from public.tools import has_post_permission
from django.shortcuts import render
from django.http.response import JsonResponse
from merchant.models import Margin_AuditLog, Apply_Project
from merchant.margin_transaction import charge_margin
import datetime
from wafuli.models import Project, InvestLog
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from account.transaction import charge_money

def admin_margin_query(request):
    return render(request,"admin_margin_query.html",)

@transaction.atomic
@has_post_permission('004')
def admin_margin(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_margin.html")
    if request.method == "POST":
        res = {}
        id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        id = int(id)
        log = Margin_AuditLog.objects.get(id=id)
        if log.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if log.type == '1':
            if type==1:
                log.audit_state = '0'
                res['code'] = 0
            elif type == 2:
                reason = request.POST.get('reason', '')
                if not reason:
                    res['code'] = -2
                    res['res_msg'] = u'传入参数不足，请联系技术人员！'
                    return JsonResponse(res)
                log.audit_state = '2'
                log.audit_reason = reason
                charge_margin(log.user, '0', log.amount, u'冲账', True, reason)
                res['code'] = 0
        if log.type == '0':
            if type==1:
                log.audit_state = '0'
                charge_margin(log.user, '0', log.amount, u'充值', True, reason)
                res['code'] = 0
            elif type == 2:
                reason = request.POST.get('reason', '')
                if not reason:
                    res['code'] = -2
                    res['res_msg'] = u'传入参数不足，请联系技术人员！'
                    return JsonResponse(res)
                log.audit_state = '2'
                log.audit_reason = reason
                charge_margin(log.user, '0', log.amount, u'冲账', True, reason)
                res['code'] = 0
        log.audit_time = datetime.datetime.now()
        log.admin_user = admin_user
        log.save(update_fields=['audit_state','audit_time','audit_reason'])
        return JsonResponse(res)

@csrf_exempt
@transaction.atomic
@has_post_permission('004')
def admin_merchant_project(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_merchant_project.html")
    elif request.method == "POST":
        res = {}
        id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        obj = Apply_Project.objects.get(id=id)
        if obj.audit_state != '1' and type != 3:
            res['code'] = 4
            res['res_msg'] = u'该项目已被审核过'
            return JsonResponse(res)
        type = int(type)
        if type==1:
            broker_rate = request.POST.get('broker_rate', '')
            if broker_rate == '':
                res['code'] = -2
                res['res_msg'] = u'佣金为必填项！'
                return JsonResponse(res)
            obj.audit_state = '0'
            obj.broker_rate = broker_rate
            res['code'] = 0
            project = Project.objects.create(title=obj.title, user=obj.user, is_official=True, category='official', is_addedto_repo=True, state='00',
                                   strategy=obj.strategy.fanshu_url(), broker_rate=broker_rate)
            obj.project = project
        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            obj.audit_state = '2'
            obj.audit_reason = reason
            res['code'] = 0
        elif type == 3:
            broker_rate = request.POST.get('broker_rate', '')
            if broker_rate == '':
                res['code'] = -2
                res['res_msg'] = u'佣金为必填项！'
                return JsonResponse(res)
            obj.broker_rate = broker_rate
            obj.project.broker_rate = broker_rate
            obj.project.save(update_fields=['broker_rate',])
            res['code'] = 0
        else:
            res['code'] = 3
            res['res_msg'] = u'type错误'
            return JsonResponse(res)    
        obj.audit_time = datetime.datetime.now()
        obj.admin_user = admin_user
        obj.save()
        return JsonResponse(res)
    
@csrf_exempt
@transaction.atomic
@has_post_permission('004')
def admin_merchant_investlog(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_project.html")
    elif request.method == "POST":
        res = {}
        id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        investlog = InvestLog.objects.get(id=id, category='merchant')
        if not investlog.audit_state in ['1']:
            res['code'] = 4
            res['res_msg'] = u'该项目非待审核状态'
            return JsonResponse(res)
        if not investlog.preaudit_state in ['0']:
            res['code'] = 4
            res['res_msg'] = u'该项目尚未被预审通过'
            return JsonResponse(res)
        reason = request.POST.get('reason')
        type = int(type)
        if not reason and type != 1:
            res['code'] = -2
            res['res_msg'] = u'原因为必填字段'
            return JsonResponse(res)
        investlog_user = investlog.user
        cash = investlog.presettle_amount
        project_title = investlog.project.title
        if type==1:
            investlog.audit_state = '0'
            translist = charge_money(investlog_user, '0', cash, project_title)
            investlog.settle_amount += cash
            translist.auditlog = investlog
            translist.save()
            res['code'] = 0
        elif type == 2:
            investlog.audit_state = '1'
            investlog.reaudit_reason = reason
            broker_amount = investlog.broker_amount
            translist = charge_margin(investlog.project.user, '0', cash, '冲账', True, '管理员拒绝')
            translist.auditlog = investlog
            translist2 = charge_margin(investlog.project.user, '0', broker_amount, '冲账', True, '管理员拒绝')
            translist2.auditlog = investlog
            translist.save(update_fields=['content_type', 'object_id'])
            translist2.save(update_fields=['content_type', 'object_id'])
            res['code'] = 0
        elif type == 3:
            investlog.audit_state = '4'
            investlog.appeal_reason = reason
        else:
            res['code'] = 3
            res['res_msg'] = u'type错误'
            return JsonResponse(res)
        investlog.audit_time = datetime.datetime.now()
        investlog.admin_user = admin_user
        investlog.presettle_amount = 0
        investlog.save()
        return JsonResponse(res)