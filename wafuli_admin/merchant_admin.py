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
from wafuli.models import Project
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt


@transaction.atomic
@has_post_permission('004')
def admin_merchant(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_merchant.html")
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
        withdrawlog = Margin_AuditLog.objects.get(id=id)
        if withdrawlog.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if type==1:
            withdrawlog.audit_state = '0'
            res['code'] = 0
            withuser = withdrawlog.user
            withuser.with_total = F('with_total')+withdrawlog.amount
            withuser.save(update_fields=['with_total'])

        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            withdrawlog.audit_state = '2'
            withdrawlog.audit_reason = reason
            charge_margin(withdrawlog.user, '0', withdrawlog.amount, u'冲账', True, reason)
            res['code'] = 0
        withdrawlog.audit_time = datetime.datetime.now()
        withdrawlog.admin_user = admin_user
        withdrawlog.save(update_fields=['audit_state','audit_time','audit_reason'])
        return JsonResponse(res)

@csrf_exempt
@transaction.atomic
@has_post_permission('004')
def admin_project(request):
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
        obj = Apply_Project.objects.get(id=id)
        if obj.audit_state != '1':
            res['code'] = 4
            res['res_msg'] = u'该项目已被审核过'
            return JsonResponse(res)
        type = int(type)
        if type==1:
            obj.audit_state = '0'
            res['code'] = 0
            project = Project.objects.create(title=obj.title, user=obj.user, is_official=True, category='official', is_addedto_repo=True, state='00',
                                   strategy=obj.strategy.fanshu_url())
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
        else:
            res['code'] = 3
            res['res_msg'] = u'type错误'
            return JsonResponse(res)    
        obj.audit_time = datetime.datetime.now()
        obj.admin_user = admin_user
        obj.save(update_fields=['audit_state','audit_time','audit_reason','project'])
        return JsonResponse(res)