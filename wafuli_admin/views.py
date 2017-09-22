#coding:utf-8
from django.shortcuts import render, redirect
from wafuli.models import InvestLog, WithdrawLog, TransList, Company, Project,\
    AdminLog
import datetime
from django.db.models import Sum, Count
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money
import logging
from account.models import MyUser, ApplyLog
from django.db.models import Q,F
from wafuli_admin.models import DayStatis, Invest_Record
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout as auth_logout
from account.varify import send_multimsg_bydhst
from xlwt import Workbook
import StringIO
from xlwt.Style import easyxf
import traceback
import xlrd
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from public.tools import has_permission
from decimal import Decimal
# Create your views here.
logger = logging.getLogger('wafuli')
def index(request):
    admin_user = request.user
    if not ( admin_user.is_authenticated() and admin_user.is_staff):
        return redirect(reverse('admin:login') + "?next=" + reverse('admin_index'))

    total = {}
    total['apply_num'] = ApplyLog.objects.count()
    dict1 = MyUser.objects.aggregate(cou=Count('id'), sumb=Sum('balance'))
    total['user_num'] = dict1.get('cou')
    total['balance'] = dict1.get('sumb') or 0
#     print TransList.objects.filter(user_investlog__investlog_type='2',user_investlog__audit_state='0').aggregate(cou=Count('id'),sum=Sum('transAmount'))
    dict_with = InvestLog.objects.filter(is_official=True,audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('return_amount'))
    total['with_count'] = dict_with.get('cou')
    total['with_total'] = dict_with.get('sum') or 0

    dict_ret = InvestLog.objects.filter(is_official=True,audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('translist__transAmount'))
    total['ret_count'] = dict_ret.get('cou')
    total['ret_total'] = dict_ret.get('sum') or 0

    return render(request,"admin_index.html", {'total':total})

def admin_apply(request):
    if request.method == "POST":
        admin_user = request.user
        res = {}
        apply_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        type = int(type)
        if not apply_id or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        apply = ApplyLog.objects.get(id=apply_id)
        if type==1:
            level = request.POST.get('level', '03')
            with transaction.atomic():
                user = MyUser(mobile=apply.mobile, username=apply.username, level=level, profile=apply.profile,
                              qq_name=apply.qq_name, qq_number=apply.qq_number, qualification=apply.qualification)
                user.set_password(apply.password)
                user.save()
                apply.audit_state = '0'
                apply.level = level
                apply.audit_time = datetime.datetime.now()
                apply.admin_user = admin_user
                apply.save()
        elif type==2:
            reason = request.POST.get('reason', '')
            apply.admin_user = admin_user
            apply.audit_time = datetime.datetime.now()
            apply.audit_state = '2'
            apply.audit_reason = reason
            apply.save()
        res['code'] = 0
        return JsonResponse(res)
    else:
        return render(request,"admin_apply.html",)
def admin_office(request):
    return render(request,"admin_office.html",)
def admin_private(request):
    return render(request,"admin_private.html",)

@transaction.atomic
@has_permission('002')
def admin_invest(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_project'))
        item_list = InvestLog.objects.filter(is_official=True, time__lt=datetime.date.today()).values_list('project_id').distinct().order_by('project_id')
        project_list = ()
        for item in item_list:
            project_list += item
        projects = Project.objects.filter(id__in=project_list)
        unaudited_pronames = []
        for project in projects:
            unaudited_pronames.append(project.title)
        return render(request,"admin_project.html", {'unaudited_pronames':unaudited_pronames})
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        investlog_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not investlog_id or type==1 and not cash or type==2 and not reason or type!=1 and type!=2:
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
            if investlog.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if investlog.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                translist = charge_money(investlog_user, '0', cash, project_title)  #jzy
                investlog.audit_state = '0'
                investlog.settle_amount = cash
                translist.investlog = investlog
                translist.save(update_fields=['investlog'])
                res['code'] = 0
        else:
            investlog.audit_state = '2'
            investlog.audit_reason = reason
            res['code'] = 0

        if res['code'] == 0:
            investlog.audit_time = datetime.datetime.now()
            investlog.admin_user = admin_user
            investlog.save()
        return JsonResponse(res)


def get_admin_project_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_project')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0 or not state:
        raise Http404
    item_list = []

    item_list = InvestLog.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))

    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    mobile_sub = request.GET.get("mobile_sub", None)
    if mobile_sub:
        item_list = item_list.filter(invest_account=mobile_sub)

    usertype = request.GET.get("usertype",0)
    usertype= int(usertype)
    if usertype == 1:
        item_list = item_list.filter(user__is_channel=False)
    elif usertype == 2:
        item_list = item_list.filter(user__is_channel=True)
        chalevel = request.GET.get("chalevel","")
        print chalevel
        if chalevel:
            item_list = item_list.filter(user__channel__level=chalevel)

    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(project__company__name__contains=companyname)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(project__title__contains=projectname)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)

    task_type = ContentType.objects.get_for_model(Project)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(investlog_type='1', audit_state=state).select_related('user')
    if state=='1':
        item_list=item_list.order_by('time')
    else:
        item_list=item_list.order_by('audit_time')
    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        project = con.content_object
        i = {"username":con.user.username if not con.user.is_channel else con.user.channel.qq_number,
             "mobile":con.user.mobile,
             "usertype":u"普通用户" if not con.user.is_channel else u"渠道："+ con.user.channel.level,
             "type":con.content_object.get_type(),
             "company":project.company.name if project.company else u"无",
             "project":project.title,
             "mobile_sub":con.invest_account,
             "remark_sub":con.remark,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "invest_time":con.invest_time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "ret_amount":u'无' if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount/100.0,
             "score":u'无' if con.audit_state!='0' or not con.score_translist.exists() else con.score_translist.first().transAmount,
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
             "invest_amount": con.invest_amount,
             "term": con.invest_term,
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
def export_invest_excel(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    state = request.GET.get("state",'1')
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
    usertype = request.GET.get("usertype",0)
    usertype= int(usertype)
    if usertype == 1:
        item_list = item_list.filter(user__is_channel=False)
    elif usertype == 2:
        item_list = item_list.filter(user__is_channel=True)
        chalevel = request.GET.get("chalevel","")
        print usertype,chalevel
        if chalevel:
            item_list = item_list.filter(user__channel__level=chalevel)
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(project__company__name__contains=companyname)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(project__title__contains=projectname)
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    task_type = ContentType.objects.get_for_model(Project)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(investlog_type='1', audit_state=state).select_related('user').order_by('time')
    data = []
    for con in item_list:
        project = con.content_object
        project_name=project.title
        mobile_sub=con.invest_account
        invest_time=con.invest_time
        id=con.id
        remark= con.remark
        invest_amount= con.invest_amount
        term=con.invest_term
        user_mobile = con.user.mobile if not con.user.is_channel else con.user.channel.qq_number
        user_type = u"普通用户" if not con.user.is_channel else u"渠道："+ con.user.channel.level
        result = ''
        return_amount = ''
        reason = ''
        if con.audit_state=='0':
            result = u'是'
            if con.translist.exists():
                return_amount = str(con.translist.first().transAmount/100.0)
        elif con.audit_state=='2':
            result = u'否'
            if con.audited_logs.exists():
                reason = con.audited_logs.first().reason
        data.append([id, project_name, invest_time, user_mobile,user_type, mobile_sub, term,
                     invest_amount, remark, result, return_amount, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'投资日期', u'挖福利账号', u'用户类型', u'注册手机号' ,u'投资期限' ,u'投资金额', u'备注',
                 u'审核通过',u'返现金额',u'拒绝原因']
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
    response['Content-Disposition'] = 'attachment; filename=待审核记录.xls'
    response.write(sio.getvalue())
    return response

def export_charge_excel(request):
    user = request.user
    item_list = []
    item_list = TransList.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    state = request.GET.get("state",'1')
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(admin_investlog__admin_user__username=adminname)
    charge_reason = request.GET.get("charge_reason", None)
    if charge_reason:
        item_list = item_list.filter(reason__contains=charge_reason)
    item_list = item_list.order_by('time')
    data = []
    for con in item_list:
        id=con.id
        user = con.user.username
        user_mobile = con.user.mobile if not con.user.is_channel else con.user.channel.qq_number
        time = con.time.strftime("%Y-%m-%d %H:%M")
        initAmount = con.initAmount/100.0
        transAmount = ('+' if con.transType=='0' else '-') + str(con.transAmount/100.0)
        reason= con.reason
        remark = con.remark
        adminname = u'无' if not con.admin_investlog else con.admin_investlog.admin_user.username
        data.append([id, user, user_mobile, time, initAmount,transAmount, reason, remark,
                     adminname])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'用户名',u'手机号', u'时间', u'初始余额', u'变动值' ,u'变动原因' ,u'备注', u'操作管理员']
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
    response['Content-Disposition'] = 'attachment; filename=待审核记录.xls'
    response.write(sio.getvalue())
    return response

@csrf_exempt
@has_permission('002')
def import_invest_excel(request):
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
    if ncols!=12:
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
                elif j==9:
                    result = cell.value.strip()
                    if result == u"是":
                        result = True
                        temp.append(True)
                    elif result == u"否":
                        result = False
                        temp.append(False)
                    else:
                        raise Exception(u"审核结果必须为是或否。")
                elif j==10:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    elif result:
                        raise Exception(u"审核结果为是时，返现金额不能为空或零。")
                    temp.append(return_amount)
                elif j==11:
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
                if investlog.audit_state != '1' or investlog.translist.exists():
                    continue
                investlog_user = investlog.user
                translist = None
                if result:
                    amount = row[3]
                    translist = charge_money(investlog_user, '0', amount, row[1])
                    if translist:
                        investlog.audit_state = '0'
                        investlog.settle_amount = amount
                        translist.user_investlog = investlog
                        translist.save(update_fields=['investlog'])
                    else:
                        logger.error(u"Charging cash is failed!!!")
                        logger.error("InvestLog:" + str(id) + u" 现金记账失败，请检查原因！！！！")
                        continue
                else:
                    investlog.audit_state = '2'
                    investlog.audit_reason = reason
                investlog.audit_time = datetime.datetime.now()
                investlog.admin_user = admin_user
                investlog.save(update_fields=['audit_state','audit_time','settle_amount','admin_user'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)

@transaction.atomic
@has_permission("005")
def admin_user(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_user'))
        return render(request,"admin_user.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('005'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        user_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        type = int(type)
#         if not user_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
#             res['code'] = -2
#             res['res_msg'] = u'传入参数不足，请联系技术人员！'
#             return JsonResponse(res)
        obj_user = MyUser.objects.get(id=user_id)
        if type==1:
            pcash = request.POST.get('pcash', 0)
            mcash = request.POST.get('mcash', 0)
            if not pcash:
                pcash = 0
            if not mcash:
                mcash = 0
            reason = request.POST.get('reason', '')
            if not pcash and not mcash or pcash and mcash or not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            try:
                pcash = Decimal(pcash)
                mcash = Decimal(mcash)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if pcash < 0 or mcash < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            translist = None
            if pcash > 0:
                translist = charge_money(obj_user, '0', pcash, reason)
            elif mcash > 0:
                translist = charge_money(obj_user, '1', mcash, reason)
            adminlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, type='1')
            translist.adminlog = adminlog
            translist.save(update_fields=['adminlog'])
            res['code'] = 0
            

        elif type == 2:
            obj_user.is_active = False
            obj_user.save(update_fields=['is_active'])
            auth_logout(request)
            admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='2', remark=u"加黑")
            res['code'] = 0
        elif type == 3:
            obj_user.is_active = True
            obj_user.save(update_fields=['is_active'])
            admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='2', remark=u"去黑")
            res['code'] = 0
        elif type == 4:
            level = request.POST.get('level')
            if level:
                obj_user.channel.level=level
                obj_user.channel.save(update_fields=['level'])
                admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='3', remark=str(level))
                res['code'] = 0
            else:
                res['code'] = -6
                res['res_msg'] = u"没有level"
        return JsonResponse(res)

def get_admin_user_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'0')

    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = MyUser.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(date_joined__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(this_login_time__range=(s,e))

    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(username=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(mobile=mobile)

    inviter_name = request.GET.get("inviter_name", None)
    if inviter_name:
        item_list = item_list.filter(inviter__username=inviter_name)

    inviter_mobile = request.GET.get("inviter_mobile", None)
    if inviter_mobile:
        item_list = item_list.filter(inviter__mobile=inviter_mobile)

    if state=='1':
        item_list = item_list.filter(is_active=False)
    elif state=='2':
        item_list = item_list.filter(is_active=True)
    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        inviter_username = u'无'
        inviter_mobile = u'无'
        inviter = con.inviter
        if inviter:
            inviter_username = inviter.username
            inviter_mobile = inviter.mobile

        card_number = u'无'
        real_name = u'无'
        if con.user_bankcard.exists():
            card = con.user_bankcard.first()
            card_number = card.card_number
            real_name = card.real_name

        recent_login_time = u'无'
        if con.this_login_time:
            recent_login_time = con.this_login_time.strftime("%Y-%m-%d %H:%M")
        i = {"username":con.username,
             "mobile":con.mobile,
             "email":con.email,
             "card_number":card_number,
             "real_name":real_name,
             # "zhifubao":con.zhifubao,
             # "zhifubao_name":con.zhifubao_name,
             "time":con.date_joined.strftime("%Y-%m-%d %H:%M"),
             'recent_login_time':recent_login_time,
             "inviter_name":inviter_username,
             "inviter_mobile":inviter_mobile,
             "balance":con.balance/100.0,
             "is_black":u'否' if con.is_active else u'是',
             "id":con.id,
             "opertype":u'加黑' if con.is_active else u'去黑',
             "opertype_channel":u'撤销渠道' if con.is_channel else u'赋予渠道权限',
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@transaction.atomic
@has_permission('004')
def admin_withdraw(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_withdraw.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        withdraw_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not withdraw_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        withdraw_id = int(withdraw_id)
        withdrawlog = WithdrawLog.objects.get(id=withdraw_id)
        if withdrawlog.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if type==1:
            withdrawlog.audit_state = '0'
            res['code'] = 0

        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            withdrawlog.audit_state = '2'
            withdrawlog.audit_reason = reason
            translist = charge_money(withdrawlog.user, '0', withdrawlog.amount, u'冲账', reverse=True)
            res['code'] = 0
        withdrawlog.audit_time = datetime.datetime.now()
        withdrawlog.admin_user = admin_user
        withdrawlog.save(update_fields=['audit_state','audit_time','audit_reason'])
        return JsonResponse(res)

def get_admin_with_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_withdraw')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')

    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404

    item_list = WithdrawLog.objects.filter(audit_state=state).select_related('user').order_by('submit_time','amount')
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))

    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    card_number = request.GET.get("card_number", None)
    if card_number:
        item_list = item_list.filter(user__user_bankcard__card_number=card_number)

    real_name = request.GET.get("real_name", None)
    if real_name:
        item_list = item_list.filter(user__user_bankcard__real_name=real_name)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)

    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        obj_user = con.user

        bank = u'无'
        card_number = u'无'
        real_name = u'无'
        if obj_user.user_bankcard.exists():
            card = obj_user.user_bankcard.first()
            bank = card.get_bank_display()
            card_number = card.card_number
            real_name = card.real_name
        i = {"username":obj_user.username,
             "mobile":obj_user.mobile,
             "userlevel":con.user.level,
             "balance":obj_user.balance,
             "bank":bank,
             "real_name":real_name,
             "card_number":card_number,
             "amount":con.amount,
             "time":con.submit_time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if not con.admin_user else admin_user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "id":con.id,
             "reason": con.audit_reason,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
def export_withdraw_excel(request):
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        raise Http404
    state = request.GET.get("state",'1')
    item_list = InvestLog.objects.filter(investlog_type='2', audit_state=state).select_related('user').order_by('time','invest_amount')
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))

    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    card_number = request.GET.get("card_number", None)
    if card_number:
        item_list = item_list.filter(user__user_bankcard__card_number=card_number)

    real_name = request.GET.get("real_name", None)
    if real_name:
        item_list = item_list.filter(user__user_bankcard__real_name=real_name)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)

    data = []

    for con in item_list:
        obj_user = con.user
        bank=''
        real_name = ''
        card_number = ''
        if obj_user.user_bankcard.exists():
            card = obj_user.user_bankcard.first()
            bank = card.get_bank_display()
            real_name = card.real_name
            card_number = card.card_number
        username = obj_user.username
        mobile = obj_user.mobile
        balance = obj_user.balance/100.0
        time=con.time
        id=con.id
        remark= con.remark
        amount= con.invest_amount/100.0
        state=con.get_audit_state_display()
        user_mobile = obj_user.qq_number
        user_level = obj_user.level
        result = ''
        reason = ''
        if con.audit_state=='0':
            result = u'是'
        elif con.audit_state=='2':
            result = u'否'
            if con.audited_logs.exists():
                reason = con.audited_logs.first().reason
        data.append([id, username, mobile, user_type, balance, bank, real_name, card_number, amount,
                     time, result, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'用户名',u'手机号', u'用户类型', u'账户余额', u'开户行', u'实名' ,u'银行卡号' ,u'申请提现金额', u'申请时间',
                 u'审核结果',u'拒绝原因']
    for i in range(len(title_row)):
        ws.write(0,i,title_row[i])
    row = len(data)
    style1 = easyxf(num_format_str='YY/MM/DD')
    for i in range(row):
        lis = data[i]
        col = len(lis)
        for j in range(col):
            if j==9:
                ws.write(i+1,j,lis[j],style1)
            else:
                ws.write(i+1,j,lis[j])
    sio = StringIO.StringIO()
    w.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=提现记录.xls'
    response.write(sio.getvalue())

    return response

@csrf_exempt
@has_permission('004')
def import_withdraw_excel(request):
    admin_user = request.user
    if not ( admin_user.is_authenticated() and admin_user.is_staff):
        raise Http404
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
    if ncols!=12:
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
                elif j==10:
                    result = cell.value.strip()
                    if result == u"是":
                        result = True
                        temp.append(True)
                    elif result == u"否":
                        result = False
                        temp.append(False)
                    else:
                        raise Exception(u"审核结果必须为是或否。")
                elif j==11:
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
    suc_num = 0
    try:
        for row in rtable:
            with transaction.atomic():
                id = row[0]
                result = row[1]
                reason = row[2]
                withdrawlog = WithdrawLog.objects.get(id=id)
                if withdrawlog.audit_state != '1':
                    continue
                withdrawlog_user = withdrawlog.user
                if result:
                    withdrawlog.audit_state = '0'
                else:
                    if not reason:
                        raise Exception(u"拒绝原因缺失")
                    withdrawlog.audit_state = '2'
                    withdrawlog.audit_reason = reason
                    translist = charge_money(withdrawlog.user, '0', withdrawlog.amount, u'冲账', reverse=True)
                withdrawlog.audit_time = datetime.datetime.now()
                withdrawlog.admin_user = admin_user
                withdrawlog.save(update_fields=['audit_state','audit_time','audit_reason','admin_user'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)


def admin_charge(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_charge'))
        return render(request,"admin_charge.html")

def get_admin_charge_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_charge')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = TransList.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))

    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(admin_investlog__admin_user__username=adminname)

    charge_reason = request.GET.get("charge_reason", None)
    if charge_reason:
        item_list = item_list.filter(reason__contains=charge_reason)

    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "time":con.time.strftime("%Y-%m-%d %H:%M"),
             "init_amount":con.initAmount/100.0,
             "charge_amount":('+' if con.transType=='0' else '-') + str(con.transAmount/100.0),
             "reason": con.reason,
             "remark": con.remark,
             "admin_user":u'无' if not con.admin_investlog else con.admin_investlog.admin_user.username,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)


def admin_investrecord(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_investrecord'))
        return render(request,"admin_investrecord.html")
def get_admin_investrecord_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_investrecord')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = Invest_Record.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    amountfrom = request.GET.get("amountfrom", None)
    amountto = request.GET.get("amountto", None)
    if amountfrom and amountto:
        af = request.GET.get("amountfrom", 0)
        at = request.GET.get("amountto", 0)
        item_list = item_list.filter(invest_amount__range=(af,at))
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user_name=username)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(invest_mobile=mobile)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(invest_company__contains=projectname)

    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        card_number = u'无'
        if con.card_number:
            card_number = con.card_number
        i = {
             "invest_date": con.invest_date.strftime("%Y-%m-%d") if con.invest_date else '',
             'invest_company':con.invest_company,
             'qq_number':con.qq_number,
             "user_name":con.user_name,
             "card_number":card_number,
             "invest_mobile":con.invest_mobile,
             'invest_period':con.invest_period,
             'invest_amount':con.invest_amount,
             'return_amount':con.return_amount,
             'wafuli_account':con.wafuli_account,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def send_multiple_msg(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_investrecord')
        return JsonResponse(res)
    if not user.has_admin_perms('007'):
        res['code'] = -5
        res['res_msg'] = u'您没有操作权限！'
        return JsonResponse(res)
    content = request.POST.get('content')
    if not content or len(content)==0:
        res['code'] = -6
        res['res_msg'] = u'短信内容不能为空！'
        return JsonResponse(res)
    phones = request.POST.get('phones')
    phone_list = json.loads(phones)
#     item_list = Invest_Record.objects.all()
#     startTime = request.POST.get("startTime", None)
#     endTime = request.POST.get("endTime", None)
#     if startTime and endTime:
#         s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
#         e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
#         item_list = item_list.filter(invest_date__range=(s,e))
#     amountfrom = request.POST.get("amountfrom", None)
#     amountto = request.POST.get("amountto", None)
#     if not amountfrom is None and not amountto is None:
#         item_list = item_list.filter(invest_amount__range=(amountfrom,amountto))
#     username = request.POST.get("username", None)
#     if username:
#         item_list = item_list.filter(user_name=username)
#
#     mobile = request.POST.get("mobile", None)
#     if mobile:
#         item_list = item_list.filter(invest_mobile=mobile)
#
#     projectname = request.POST.get("projectname", None)
#     if projectname:
#         item_list = item_list.filter(invest_company__contains=projectname)
#     phone_set = set(phone_list)
#     for item in phone_list:
#         phone = item.invest_mobile
#         if phone and len(phone)==11:
#             phone_set.add(phone)
    if len(phone_list)>0:
        phone_list = list(set(phone_list))
        length = len(phone_list)
        times = length/500
        treg = 0
        tnum = 0
        if length%500 > 0:
            times += 1
        for t in range(times):
            frag_list = phone_list[t*500:t*500+500]
            phones = ','.join(frag_list)
            logger.info("Sending mobile messages to users:" + phones + "; content:" + content);
            reg = send_multimsg_bydhst(phones, content)
            if reg==0:
                tnum += len(frag_list)
            else:
                treg = 1
        if treg==0:
            res['code'] = 0
            res['num'] = tnum
        else:
            res['code'] = -1
            res['res_msg'] = u"发送短信失败，实际发送数量：" + str(tnum)
    else:
        res['code'] = 0
        res['res_msg'] = u"没有选中任何手机号码"
    return JsonResponse(res)

