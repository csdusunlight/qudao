#coding:utf-8
'''
Created on 2018年1月17日

@author: lch
'''
from django.db import transaction
from public.tools import has_post_permission
from django.shortcuts import render
from django.http.response import JsonResponse, Http404, HttpResponse
from merchant.models import Margin_AuditLog, Apply_Project
from merchant.margin_transaction import charge_margin
import datetime
from wafuli.models import Project, InvestLog
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from account.transaction import charge_money
from django.contrib.auth.decorators import login_required
from xlwt.Workbook import Workbook
from xlwt.Style import easyxf
import StringIO
import xlrd
from decimal import Decimal
import traceback

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
        reason = request.POST.get('reason', '')
        if log.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if log.type == '1':
            if type==1:
                log.audit_state = '0'
                res['code'] = 0
            elif type == 2:
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
                res['code'] = 0
        log.audit_time = datetime.datetime.now()
        log.admin_user = admin_user
        log.save(update_fields=['audit_state','audit_time','audit_reason'])
        return JsonResponse(res)

@csrf_exempt
@transaction.atomic
@has_post_permission('100')
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
            project = Project.objects.create(title=obj.title, user=obj.user, is_official=True, category='merchant', is_addedto_repo=True, state='00',
                                   strategy=obj.strategy.fanshu_url(), broker_rate=broker_rate, doc=obj.strategy)
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
@has_post_permission('100')
def admin_merchant_investlog(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_merchant_investlog.html")
    elif request.method == "POST":
        res = {}
        id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        type = int(type)
        if not id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        investlog = InvestLog.objects.get(id=id, category='merchant')
        if not investlog.audit_state in ['1'] and type!=3:
            res['code'] = 4
            res['res_msg'] = u'该项目非待审核状态'
            return JsonResponse(res)
        if not investlog.preaudit_state in ['0'] and type!=3:
            res['code'] = 4
            res['res_msg'] = u'该项目尚未被预审通过'
            return JsonResponse(res)
        reason = request.POST.get('reason')
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
            investlog.preaudit_state = '1'
            investlog.audit_reason = reason
            broker_amount = investlog.broker_amount
            if cash>0:
                translist = charge_margin(investlog.project.user, '0', cash, '冲账', True, '管理员拒绝')
                translist.auditlog = investlog
                translist.save(update_fields=['content_type', 'object_id'])
            if broker_amount>0:    
                translist2 = charge_margin(investlog.project.user, '0', broker_amount, '冲账', True, '管理员拒绝')
                translist2.auditlog = investlog
                translist2.save(update_fields=['content_type', 'object_id'])
            res['code'] = 0
        elif type == 3:
            res['code'] = 0
            investlog.audit_state = '4'
            investlog.appeal_reason = reason
        else:
            res['code'] = 3
            res['res_msg'] = u'type错误'
            return JsonResponse(res)
        investlog.audit_time = datetime.datetime.now()
        investlog.admin_user = admin_user
#         investlog.presettle_amount = 0
        investlog.save()
        return JsonResponse(res)
    
@login_required
def admin_export_merchant_investlog(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects.filter(category='merchant')
    if not user.is_staff:
        raise Http404
    investtime_0 = request.GET.get("investtime_0", None)
    investtime_1 = request.GET.get("investtime_1", None)
    submittime_0 = request.GET.get("submittime_0", None)
    submittime_1 = request.GET.get("submittime_1", None)
    audittime_0 = request.GET.get("audittime_0", None)
    audittime_1 = request.GET.get("audittime_1", None)
    state = request.GET.get("audit_state",'1')
    submit_type = request.GET.get('submit_type', '0')
    if investtime_0 and investtime_1:
        s = datetime.datetime.strptime(investtime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(investtime_1,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    if submittime_0 and submittime_1:
        s = datetime.datetime.strptime(submittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(submittime_1,'%Y-%m-%d')
        item_list = item_list.filter(submit_time__range=(s,e))
    if audittime_0 and audittime_1:
        s = datetime.datetime.strptime(audittime_0,'%Y-%m-%d %H:%M')
        e = datetime.datetime.strptime(audittime_1,'%Y-%m-%d %H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
    qq_number = request.GET.get("qq_number", None)
    if qq_number:
        item_list = item_list.filter(user__qq_number=qq_number)
    mobile = request.GET.get("user_mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
    userlevel = request.GET.get("level",None)
    if userlevel:
        item_list = item_list.filter(user__level=userlevel)
    is_official = request.GET.get("is_official",None)
    if is_official:
        item_list = item_list.filter(is_official=is_official)
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(project__company__name__contains=companyname)
    invest_mobile = request.GET.get("invest_mobile", None)
    if invest_mobile:
        item_list = item_list.filter(invest_mobile=invest_mobile)
    projectname = request.GET.get("project_title_contains", None)
    if projectname:
        item_list = item_list.filter(project__title__contains=projectname)
    adminname = request.GET.get("admin_user", None)
    if adminname:
        item_list = item_list.filter(admin_user__username=adminname)
    if submit_type=='1' or submit_type=='2':
        item_list = item_list.filter(submit_type=submit_type)
    item_list = item_list.filter(audit_state=state).select_related('user', 'project').order_by('submit_time')
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
        if con.audit_state=='0':
            result = u'是'
            settle_amount = str(con.settle_amount)
        elif con.audit_state=='2':
            result = u'否'
        data.append([id, project_name, invest_date, qq_number,user_level, settle_price, invest_mobile, invest_name, term,
                     invest_amount, submit_type, remark, result, settle_amount, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'投资日期', u'QQ', u'用户类型', u'结算价格', u'投资手机号', u'投资姓名' ,u'投资期限' ,u'投资金额',u'投资类型', u'备注',
                 u'审核通过',u'结算金额',u'拒绝原因']
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
    response['Content-Disposition'] = 'attachment; filename=投资记录表.xls'
    response.write(sio.getvalue())
    return response

@csrf_exempt
@has_post_permission('002')
def admin_import_merchant_investlog(request):
    admin_user = request.user
    ret = {'code':-1}
    file = request.FILES.get('file')
#     print file.name
    with open('./out.xls', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    data = xlrd.open_workbook('out.xls')
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    if ncols!=15:
        ret['msg'] = u"文件格式与模板不符，请在导出的待审核记录表中更新后将文件导入！"
        return JsonResponse(ret)
    rtable = []
    mobile_list = []
    try:
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
                elif j==12:
                    result = cell.value.strip()
                    if result == u"是":
                        result = 1
                    elif result == u"否":
                        result = 2
                    elif result == u"复审":
                        result = 3
                    else:
                        raise Exception(u"审核结果必须为是,否或复审。")
                    temp.append(result)
                elif j==13:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    elif result==1:
                        raise Exception(u"审核结果为是时，返现金额不能为空或零。")
                    temp.append(return_amount)
                elif j==14:
                    reason = cell.value
                    temp.append(reason)
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
    try:
        for row in rtable:
            with transaction.atomic():
                id = row[0]
                result = row[2]
                reason = row[4]
                investlog = InvestLog.objects.get(id=id)
                if not investlog.audit_state in ['1','3'] or investlog.translist.exists():
                    continue
                investlog_user = investlog.user
                translist = None
                if result==1:
                    amount = row[3]
                    translist = charge_money(investlog_user, '0', amount, row[1])
                    investlog.audit_state = '0'
                    investlog.settle_amount = amount
                    translist.auditlog = investlog
                    translist.save()
#                     #活动插入
#                     on_audit_pass(request, investlog)
#                     #活动插入结束
                elif result==2:
                    investlog.audit_state = '2'
                elif result==3:
                    investlog.audit_state = '3'
                investlog.audit_reason = reason    
                investlog.audit_time = datetime.datetime.now()
                investlog.admin_user = admin_user
                investlog.save(update_fields=['audit_state','audit_time','settle_amount','audit_reason','admin_user'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)