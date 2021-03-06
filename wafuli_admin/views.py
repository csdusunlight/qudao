#coding:utf-8
from django.shortcuts import render, redirect
from wafuli.models import InvestLog, WithdrawLog, TransList, Company, Project,\
    AdminLog, SubscribeShip
import datetime
from django.db.models import Sum, Count
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money
import logging
from account.models import MyUser, AdminPermission,Message,ApplyLogForChannel,ApplyLogForFangdan
from django.db.models import Q,F
from wafuli_admin.models import DayStatis, Invest_Record
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout as auth_logout
from account.varify import send_multimsg_bydhst, sendmsg_bydhst
from xlwt import Workbook
import StringIO
from xlwt.Style import easyxf
import traceback
import xlrd
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from public.tools import has_post_permission, has_permission, send_mobilemsg_multi
from decimal import Decimal
from weixin.tasks import sendWeixinNotify
from merchant.margin_transaction import charge_margin
from coupon.views import on_register
from django_redis import get_redis_connection
from django.core.cache import cache
from coupon.models import UserCoupon
from finance.pay import batch_transfer_to_zhifubao
# Create your views here.
logger = logging.getLogger('wafuli')
def index(request):
    admin_user = request.user
    if not ( admin_user.is_authenticated() and admin_user.is_staff):
        return redirect(reverse('admin:login') + "?next=" + reverse('admin_index'))

    total = {}
    total['apply_num'] = ApplyLogForChannel.objects.count()
    total['apply_success'] = ApplyLogForChannel.objects.filter(audit_state='0').count()
    dict1 = MyUser.objects.aggregate(cou=Count('id'), sumb=Sum('balance'))
    total['user_num'] = MyUser.objects.count()
    total['balance'] = dict1.get('sumb') or 0
#     print TransList.objects.filter(user_investlog__investlog_type='2',user_investlog__audit_state='0').aggregate(cou=Count('id'),sum=Sum('transAmount'))
    dict_with = WithdrawLog.objects.filter(audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('amount'))
    total['with_count'] = dict_with.get('cou')
    total['with_total'] = dict_with.get('sum') or 0

    dict_ret = InvestLog.objects.filter(category='official',audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('settle_amount'))
    total['ret_count'] = dict_ret.get('cou')
    total['ret_total'] = dict_ret.get('sum') or 0

    return render(request,"admin_index.html", {'total':total})

def admin_merchant_look(request):
    return render(request,"admin_merchant_look.html", {})



import time

@has_post_permission('052')

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
        current_applyforchannel = ApplyLogForChannel.objects.get(id=apply_id)
        currentuser = current_applyforchannel.user
        if type==1:
            level = request.POST.get('level', '03')
            with transaction.atomic():
                ####################
                reason = "success"
                nowtime = datetime.datetime.now()
                Message.objects.create(user=currentuser, title="渠道申请审核反馈", is_read=False,
                                       content=u"尊敬的用户：您申请成为渠道用户成功！")
                currentuser.is_channel='1'
                currentuser.level=level
                currentuser.num_message_sync+=1
                currentuser.save(update_fields=['is_channel','level','num_message_sync'])
                current_applyforchannel.audit_time = nowtime
                current_applyforchannel.audit_state = '0'
                current_applyforchannel.admin_user = admin_user
                current_applyforchannel.save(update_fields=['audit_time', 'audit_state', 'admin_user'])
                AdminLog.objects.create(admin_user=admin_user, custom_user=currentuser, remark=reason, type='3')
                sendmsg_bydhst(currentuser.mobile, u"您申请成为渠道用户成功！")
                res['code'] = 0
                ####################
        elif type==2:
            reason = request.POST.get('reason', '')
            nowtime = datetime.datetime.now()
            Message.objects.create(user=currentuser, title="渠道申请审核反馈", is_read=False,
                                   content=u"尊敬的用户：您申请成为渠道用户失败。被拒绝原因如下：" + reason)  # 写入审核原因，加个字段
            currentuser.is_channel = '０'
            currentuser.num_message_sync += 1
            currentuser.save(update_fields=['is_channel','num_message_sync'])
            current_applyforchannel.audit_time = nowtime
            current_applyforchannel.audit_state = '2'
            current_applyforchannel.audit_reason = reason
            current_applyforchannel.admin_user = admin_user
            current_applyforchannel.save(update_fields=['audit_time', 'audit_state', 'admin_user','audit_reason'])
            AdminLog.objects.create(admin_user=admin_user, custom_user=currentuser, remark=reason, type='3')
            sendmsg_bydhst(currentuser.mobile, u"您申请成为渠道用户失败" + reason)
            res['code'] = 0
        res['code'] = 0
        return JsonResponse(res)
    else:
        return render(request,"admin_apply.html",)

@csrf_exempt
@has_post_permission('054')
def admin_apply_for_fangdan_permission(request):
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
        current_applyforfangdan = ApplyLogForFangdan.objects.get(id=apply_id)
        currentuser = current_applyforfangdan.user
        if type==1:
            with transaction.atomic():
                reason = "success"
                nowtime=datetime.datetime.now()
                Message.objects.create(user=currentuser, title="放单权限申请审核反馈", is_read=False,
                                       content=u"尊敬的用户：您申请放单权限成功！")
                currentuser.is_merchant='1'
                currentuser.save(update_fields=['is_merchant',])
                current_applyforfangdan.audit_time = nowtime
                current_applyforfangdan.audit_state = '0'
                current_applyforfangdan.admin_user = admin_user
                current_applyforfangdan.save(update_fields=['audit_time', 'audit_state', 'admin_user'])
                AdminLog.objects.create(admin_user=admin_user, custom_user=currentuser, remark=reason, type='3',
                                        time=nowtime)
                sendmsg_bydhst(currentuser.mobile, u"尊敬的用户：您申请放单权限成功！")
                res['code'] = 0
                ####################
        elif type==2:
            reason = request.POST.get('reason', '')
            nowtime = datetime.datetime.now()
            Message.objects.create(user=currentuser, title="放单权限申请审核反馈", is_read=False,
                                   content=u"尊敬的用户：您申请放单权限失败。被拒绝原因如下：" + reason)  # 写入审核原因，加个字段
            current_applyforfangdan.audit_time = nowtime
            current_applyforfangdan.audit_state = '2'
            current_applyforfangdan.audit_reason = reason
            current_applyforfangdan.admin_user = admin_user
            current_applyforfangdan.save(update_fields=['audit_time', 'audit_state', 'admin_user','audit_reason'])
            AdminLog.objects.create(admin_user=admin_user, custom_user=currentuser, remark=reason, type='3',
                                    time=nowtime)
            sendmsg_bydhst(currentuser.mobile, u"尊敬的用户：您申请放单权限失败" + reason)
            res['code'] = 0
        res['code'] = 0
        return JsonResponse(res)
    else:
        return render(request,"admin_merchant_apply.html",)
# def admin_office(request):
#     return render(request,"admin_office.html",)
def admin_private(request):
    return render(request,"admin_private.html",)

@transaction.atomic
@has_post_permission('002')
def admin_invest(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_invest'))
        item_list = InvestLog.objects.filter(category='official', audit_state__in=['1','3'], submit_time__lt=datetime.date.today()).values_list('project_id').distinct().order_by('project_id')
        print item_list
        project_list = ()
        for item in item_list:
            project_list += item
        projects = Project.objects.filter(id__in=project_list)
        unaudited_pronames = []
        for project in projects:
            unaudited_pronames.append(project.title)
        return render(request,"admin_office.html", {'unaudited_pronames':unaudited_pronames})
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        investlog_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', '')
        type = int(type)
        if not investlog_id or type==1 and not cash or not type in [1, 2, 3, 4]:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
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
            if not investlog.audit_state in ['1', '3']:
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if investlog.audit_state == '1' and investlog.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                translist = charge_money(investlog_user, '0', cash, project_title, auditlog=investlog)
                investlog.audit_state = '0'
                investlog.settle_amount += cash
                #红包插入+++++++++++++++++++
                with cache.lock("admin_invest"):
                    users = cache.get('invest_user_set') or ''
                    user_set = set(users.split(','))  if users else set()
                    user_set.add(str(investlog_user.id))
                    cache.set('invest_user_set', ','.join(user_set))
                #红包插入+++++++++++++++++++
#                 #活动插入
#                 on_audit_pass(request, investlog)
#                 #活动插入结束
                investlog.audit_reason = reason
                res['code'] = 0
        elif type==2:
            if investlog.settle_amount == 0:
                investlog.audit_state = '2'
            investlog.audit_reason = reason
            res['code'] = 0
        elif type==3:
            investlog.audit_state = '3'
            investlog.audit_reason = reason
            res['code'] = 0
        elif type==4:
            if investlog.delta_amount > 0:
                res['code'] = 2
                res['res_msg'] = u"不得重复补差价！"
                return JsonResponse(res)
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
            if investlog.audit_state != '0':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            translist = charge_money(investlog_user, '0', cash, project_title, remark=u"补差价", auditlog=investlog)
            investlog.settle_amount += cash
            investlog.delta_amount = cash
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

@login_required
def export_investlog(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects.filter(category='official')
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
        delta_amount = con.delta_amount
        settle_price = con.get_project_price()
        reason = con.audit_reason
        submit_type = con.get_submit_type_display()
        if con.audit_state=='0':
            result = u'是'
            settle_amount = str(con.settle_amount)
        elif con.audit_state=='2':
            result = u'否'
        data.append([id, project_name, invest_date, qq_number,user_level, settle_price, invest_mobile, invest_name, term,
                     invest_amount, submit_type, remark, result, settle_amount, reason, delta_amount])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'投资日期', u'QQ', u'用户类型', u'结算价格', u'投资手机号', u'投资姓名' ,u'投资期限' ,u'投资金额',u'投资类型', u'备注',
                 u'审核通过',u'结算金额',u'拒绝原因',u'补差价']
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
@has_post_permission('002')
def import_investlog(request):
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
    if ncols!=16:
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
    user_set_temp = set()
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
                    translist = charge_money(investlog_user, '0', amount, row[1], auditlog=investlog)
                    investlog.audit_state = '0'
                    investlog.settle_amount = amount
                    #红包插入+++++++++++++++++++
                    user_set_temp.add(str(investlog_user.id))
                    #红包插入+++++++++++++++++++
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
        #红包插入+++++++++++++++++++
        with cache.lock("admin_invest"):
            users = cache.get('invest_user_set') or ''
            user_set = set(users.split(',')) if users else set()
            user_set.update(user_set_temp)
            cache.set('invest_user_set', ','.join(user_set))
        #红包插入+++++++++++++++++++
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)

@transaction.atomic
def admin_user(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_user'))
        return render(request,"admin_user.html")
    if request.method == "POST":
        res = {}
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
            if not admin_user.has_admin_perms('050'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
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
            adminlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, type='1')
            if pcash > 0:
                translist = charge_money(obj_user, '0', pcash, reason, auditlog=adminlog)
            elif mcash > 0:
                translist = charge_money(obj_user, '1', mcash, reason, auditlog=adminlog)
            res['code'] = 0


        elif type == 2:
            if not admin_user.has_admin_perms('051'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            obj_user.is_active = False
            obj_user.save(update_fields=['is_active'])
            admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='2', remark=u"加黑")
            res['code'] = 0
        elif type == 3:
            if not admin_user.has_admin_perms('051'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            obj_user.is_active = True
            obj_user.save(update_fields=['is_active'])
            admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='2', remark=u"去黑")
            res['code'] = 0
        elif type == 4:
            if not admin_user.has_admin_perms('052'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            level = request.POST.get('level')
            if level:
                obj_user.level=level
                obj_user.save(update_fields=['level'])
                admin_investlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='3', remark=str(level))
                res['code'] = 0
            else:
                res['code'] = -6
                res['res_msg'] = u"没有level"
        elif type == 5:
            if not admin_user.has_admin_perms('053'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
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
            adminlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, type='4')
            if pcash > 0:
                translist = charge_margin(obj_user, '0', pcash, reason, auditlog=adminlog)
            elif mcash > 0:
                translist = charge_margin(obj_user, '1', mcash, reason, auditlog=adminlog)
            res['code'] = 0
        elif type == 6:
            if not admin_user.has_admin_perms('054'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            obj_user.is_merchant = '1'
            obj_user.save(update_fields=['is_merchant'])
            adminlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='5')
            res['code'] = 0
        elif type == 7:
            if not admin_user.has_admin_perms('054'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            obj_user.is_merchant = '0'
            obj_user.save(update_fields=['is_merchant'])
            adminlog = AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, type='5')
            res['code'] = 0

        elif type == 8:#添加关于渠道用户被拒绝的操作，返回拒绝的消息和拒绝的原因，消息是固定的，原因是审核者填写的
            if not admin_user.has_admin_perms('052'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            user_level = request.POST.get('user_level', 0)
            user_is_allow = request.POST.get('is_allow',0)
            refuse_reason = request.POST.get('refuse_reason', 0)
            #根据传入的字段
            if user_is_allow =='1':#
                reason="success"
                nowtime = datetime.datetime.now()
                obj_user.save(is_channel=1,user_level=user_level)
                AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, type='3',time=nowtime)
                res['code'] = 0
            elif user_is_allow=='0':
                nowtime = datetime.datetime.now()
                AdminLog.objects.create(admin_user=admin_user, custom_user=obj_user, remark=refuse_reason, type='3',time=nowtime)
                res['code'] = 0
            else:
                res['code'] = -2
                res['res_msg'] = u'输入不合法！'
        elif type == 10:
            if not admin_user.has_admin_perms('056'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            try:
                perm = AdminPermission.objects.get(code='200')
            except AdminPermission.DoesNotExist:
                perm = AdminPermission.objects.create(code='200', name="支付宝打款权限")
            obj_user.admin_permissions.add(perm)
            res['code'] = 0
        elif type == 11:
            if not admin_user.has_admin_perms('056'):
                res['code'] = -5
                res['res_msg'] = u'您没有操作权限！'
                return JsonResponse(res)
            perm = AdminPermission.objects.get(code='200')
            obj_user.admin_permissions.remove(perm)
            res['code'] = 0
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
@has_post_permission('004')
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
            charge_money(withdrawlog.user, '0', withdrawlog.amount, u'冲账', True, reason, auditlog=withdrawlog)
            res['code'] = 0
        withdrawlog.audit_time = datetime.datetime.now()
        withdrawlog.admin_user = admin_user
        withdrawlog.save(update_fields=['audit_state','audit_time','audit_reason'])
        
        #发送微信通知
        if type==1:
            sendWeixinNotify.delay([(withdrawlog.user, withdrawlog),], 'withdraw_success_yhk')
        elif type==2:
            sendWeixinNotify.delay([(withdrawlog.user, withdrawlog),], 'withdraw_fail')
        #
        return JsonResponse(res)

@transaction.atomic
@has_post_permission('004')
def admin_withdraw_autoaudit(request):
    admin_user = request.user
    if request.method == "GET":
        ret = {}
        withlist = WithdrawLog.objects.filter(audit_state='1', amount__lt=50000).all()
        sub_from = request.GET.get('sub_from')
        sub_to = request.GET.get('sub_to')
        if sub_from and sub_to:
            dateform = datetime.datetime.strptime(sub_from, '%Y-%m-%dT%H:%M')
            dateto = datetime.datetime.strptime(sub_to, '%Y-%m-%dT%H:%M')
            withlist = withlist.filter(submit_time__range=(dateform, dateto))
        id_list_str = request.GET.get('id_list')
        if id_list_str:
            id_list = [ int(x) for x in id_list_str.split(',') ]
            withlist = withlist.filter(id__in=id_list)
        dic = withlist.aggregate(count=Count('id'), sum=Sum('amount'))
        ret['count'] = dic['count'] or 0
        ret['sum'] = dic['sum'] or 0
        return JsonResponse(ret)
    if request.method == "POST":
        batch_list = []
        init_withlist = []
        withlist = WithdrawLog.objects.filter(audit_state='1', amount__lt=50000).all().select_for_update()
        sub_from = request.POST.get('sub_from')
        sub_to = request.POST.get('sub_to')
        if sub_from and sub_to:
            dateform = datetime.datetime.strptime(sub_from, '%Y-%m-%dT%H:%M')
            dateto = datetime.datetime.strptime(sub_to, '%Y-%m-%dT%H:%M')
            withlist = withlist.filter(submit_time__range=(dateform, dateto))
        id_list_str = request.POST.get('id_list')
        if id_list_str:
            id_list = [ int(x) for x in id_list_str.split(',') ]
            withlist = withlist.filter(id__in=id_list)
        for obj in withlist:
            batch_list.append({
                'obj': obj,
                'payee_account':obj.user.zhifubao,
                'payee_real_name':obj.user.zhifubao_real_name,
                'amount':str(obj.amount),
                'remark':u"账户余额提现"
            })
            init_withlist.append(obj)
        ret = batch_transfer_to_zhifubao(batch_list)
        fail_id_list = []
        for item in ret['detail']:
            obj = item['obj']
            fail_id_list.append(obj.id)
            obj.except_info = item['msg']
            obj.save(update_fields=['except_info'])

        withlist.exclude(id__in=fail_id_list).update(audit_state='0', audit_time=datetime.datetime.now(),
                                                     admin_user=request.user)
        suc_withlist = filter(lambda x:x.id not in fail_id_list, init_withlist)
        suc_list = []
        for item in suc_withlist:
            suc_list.append((item.user, item))
        sendWeixinNotify.delay(suc_list, 'withdraw_success_zhifubao')
        return JsonResponse({'suc_num':ret.get('suc_num')})
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

    userlevel = request.GET.get("userlevel", None)
    if username:
        item_list = item_list.filter(user__level=userlevel)

    qq_number = request.GET.get("qq_number", None)
    if qq_number:
        item_list = item_list.filter(user__qq_number=qq_number)

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
        i = {"qq_number":obj_user.qq_number,
             "qq_name":obj_user.qq_name,
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

@login_required
def export_withdrawlog(request):
    user = request.user
    if not user.is_staff:
        raise Http404
    state = request.GET.get("audit_state",'1')
    item_list = WithdrawLog.objects.filter(audit_state=state).select_related('user').order_by('submit_time','-amount')
    submit_date_0 = request.GET.get("submit_date_0", None)
    submit_date_1 = request.GET.get("submit_date", None)
    audit_date_0 = request.GET.get("audit_date_0", None)
    audit_date_1 = request.GET.get("audit_date_1", None)
    state = request.GET.get("audit_state",'1')
    if submit_date_0 and submit_date_1:
        s = datetime.datetime.strptime(submit_date_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(submit_date_1,'%Y-%m-%d')
        item_list = item_list.filter(submit_time__range=(s,e))
    if audit_date_0 and audit_date_1:
        s = datetime.datetime.strptime(audit_date_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(audit_date_1,'%Y-%m-%d')
        item_list = item_list.filter(audit_time__range=(s,e))

    qq_number = request.GET.get("qq_number", None)
    if qq_number:
        item_list = item_list.filter(user__qq_number=qq_number)

    mobile = request.GET.get("user_mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    card_number = request.GET.get("card_number", None)
    if card_number:
        item_list = item_list.filter(user__user_bankcard__card_number=card_number)

    real_name = request.GET.get("real_name", None)
    if real_name:
        item_list = item_list.filter(user__user_bankcard__real_name=real_name)

    admin_mobile = request.GET.get("admin_mobile", None)
    if admin_mobile:
        item_list = item_list.filter(admin_user__mobile=admin_mobile)

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
        qq_number = obj_user.qq_number
        mobile = obj_user.mobile
        balance = obj_user.balance
        time=con.submit_time
        id=con.id
        amount= con.amount
        state=con.get_audit_state_display()
        user_mobile = obj_user.qq_number
        user_level = obj_user.level
        result = ''
        reason = ''
        if con.audit_state=='0':
            result = u'是'
        elif con.audit_state=='2':
            result = u'否'
            reason = con.audit_reason
        data.append([id, qq_number, mobile, user_level, balance, bank, real_name, card_number, amount,
                     time, result, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'qq号',u'手机号', u'用户级别', u'账户余额', u'开户行', u'实名' ,u'银行卡号' ,u'申请提现金额', u'申请时间',
                 u'是否审核通过',u'拒绝原因']
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
@has_post_permission('004')
def import_withdrawlog(request):
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
    suc_list = []
    fail_list = []
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
                    suc_list.append((withdrawlog_user,withdrawlog))
                else:
                    if not reason:
                        raise Exception(u"拒绝原因缺失")
                    withdrawlog.audit_state = '2'
                    withdrawlog.audit_reason = reason
                    charge_money(withdrawlog.user, '0', withdrawlog.amount, u'冲账', True, reason, auditlog=withdrawlog)
                    fail_list.append((withdrawlog_user,withdrawlog))
                withdrawlog.audit_time = datetime.datetime.now()
                withdrawlog.admin_user = admin_user
                withdrawlog.save(update_fields=['audit_state','audit_time','audit_reason','admin_user'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    #发送微信通知
    sendWeixinNotify.delay(suc_list, 'withdraw_success_yhk')
    sendWeixinNotify.delay(fail_list, 'withdraw_fail')
    #
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


def admin_send_mobile_msg(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_send_mobile_msg'))
        return render(request,"admin_send_mobile_msg.html")

def send_multiple_msg(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_send_mobile_msg')
        return JsonResponse(res)
    if not user.has_admin_perms('012'):
        res['code'] = -5
        res['res_msg'] = u'您没有操作权限！'
        return JsonResponse(res)
    content = request.POST.get('content')
    if not content or len(content)==0:
        res['code'] = -6
        res['res_msg'] = u'短信内容不能为空！'
        return JsonResponse(res)
    phones = request.POST.get('phones')
    if phones == 'all':
        phone_list = list(MyUser.objects.all().values('mobile'))
        phone_list = [ x['mobile'] for x in phone_list]
    else:
        phone_list = str(phones).split('\n')
    if len(phone_list)>0:
        tnum = send_mobilemsg_multi(phone_list, content)
        if len(phone_list)==tnum:
            res['code'] = 0
            res['num'] = tnum
        else:
            res['code'] = -1
            res['res_msg'] = u"发送短信失败，实际发送数量：" + str(tnum)
    else:
        res['code'] = 0
        res['res_msg'] = u"没有选中任何手机号码"
    return JsonResponse(res)

def award_logs(request):
    return render(request,"award_logs.html",)

def batch_withdraw_task():
    users = MyUser.objects.filter(balance__gte=10, is_autowith=True)
    for user in users:
        if not user.zhifubao:
            continue
        try:
            with transaction.atomic():
                amount = user.balance
                withdrawlog = WithdrawLog.objects.create(user=user, amount=amount, audit_state='1')
                charge_money(user, '1', amount, u'系统自动提现', auditlog=withdrawlog)
        except:
            continue
@login_required
@has_permission('004')
def batch_withdraw(request):
    if not request.user.is_staff or not request.is_ajax():
        raise Http404
    batch_withdraw_task()
    return JsonResponse({'code':0})
    
def admin_merchant_show(request):    #jzy
    return render(request,"admin_merchant_show.html",{})
def coupon_send(request):    #jzy
    return render(request,"coupon_send.html",{})
def coupon_manage(request):    #jzy
    return render(request,"coupon_manage.html",{})
def coupon_plan(request):    #jzy
    return render(request,"coupon_plan.html",{})
def admin_merchant_apply(request):    #jzy
    return render(request,"admin_merchant_apply.html",{})
def coupon_count(request):
    total = {}
    dic = UserCoupon.objects.filter(type='heyue').aggregate(count_user=Count('user', distinct=True),
                    count_coupon=Count('*'), sum=Sum('award'))
    coupon_user_total = dic.get('count_user') or 0
    coupon_total = dic.get('count_coupon') or 0
    coupon_award = dic.get('sum') or 0
    dic = UserCoupon.objects.filter(type='heyue', state='2').aggregate(count_user=Count('user', distinct=True),
                count_coupon=Count('*'), sum=Sum('award'))
    coupon_user_total_obtain = dic.get('count_user') or 0
    coupon_total_obtain = dic.get('count_coupon') or 0
    coupon_award_obtain = dic.get('sum') or 0
    dic = UserCoupon.objects.filter(type='heyue', state='1').aggregate(count_user=Count('user', distinct=True),
                count_coupon=Count('*'), sum=Sum('award'))
    coupon_user_total_unlock = dic.get('count_user') or 0
    coupon_total_unlock = dic.get('count_coupon') or 0
    coupon_award_unlock = dic.get('sum') or 0
    total['coupon_user_total'] = coupon_user_total
    total['coupon_total'] = coupon_total
    total['coupon_award'] = coupon_award
    total['coupon_user_total_unlock'] = coupon_user_total_unlock
    total['coupon_total_unlock'] = coupon_total_unlock
    total['coupon_award_unlock'] = coupon_award_unlock
    total['coupon_user_total_obtain'] = coupon_user_total_obtain
    total['coupon_total_obtain'] = coupon_total_obtain
    total['coupon_award_obtain'] = coupon_award_obtain
    return render(request,"coupon_count.html",{'total':total})

@csrf_exempt
@has_post_permission('002')
def import_delta(request):
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
    rtable = []
    mobile_list = []
    try:
        for i in range(1,nrows):
            temp = []
            for j in range(ncols):
                cell = table.cell(i,j)
                if j==0:
                    id = int(cell.value)
                    temp.append(id)
                elif j==1:
                    project = cell.value
                    temp.append(project)
                elif j==ncols-1:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    else:
                        return_amount = 0
                    temp.append(return_amount)
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
    user_set_temp = set()
    try:
        for row in rtable:
            id = row[0]
            project = row[1]
            delta = row[2]
            if delta <= 0:
                continue
            with transaction.atomic():
                try:
                    investlog = InvestLog.objects.get(id=id, delta_amount=0, audit_state='0')
                except InvestLog.DoesNotExist:
                    continue
                investlog_user = investlog.user
                charge_money(investlog_user, '0', delta, project, remark=u"补差价", auditlog=investlog)
                investlog.delta_amount = delta
                investlog.settle_amount += delta
                investlog.save(update_fields=['delta_amount', 'settle_amount'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)
