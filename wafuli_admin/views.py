#coding:utf-8
from django.shortcuts import render, redirect
from wafuli.models import UserEvent, AdminEvent, AuditLog, TransList, Company,\
    Finance, Task, Welfare, Message
import datetime
from django.db.models import Sum, Count
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money, charge_score
import logging
from account.models import MyUser, Channel
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
from account.vip import vip_judge, get_vip_bonus
import json
from django.db import transaction
from project_admin.tools import has_permission
# Create your views here.
logger = logging.getLogger('wafuli')
def index(request):
    admin_user = request.user
    if not ( admin_user.is_authenticated() and admin_user.is_staff):
        return redirect(reverse('admin:login') + "?next=" + reverse('admin_index'))
    today = datetime.date.today()
#     day = datetime.datetime.strptime('2015-01-01','%Y-%m-%d')
#     with_num_today = UserEvent.objects.filter(event_type='2',time__gte=today,audit_state='1').count()
#     with_num = UserEvent.objects.filter(event_type='2',audit_state='1').count()
#     ret_num_today = UserEvent.objects.filter(event_type='1',time__gte=today,audit_state='1').count()
#     ret_num = UserEvent.objects.filter(event_type='1',audit_state='1').count()
    query = UserEvent.objects.filter(audit_state='1').values('event_type')\
                .annotate(sum=Count('*')).order_by()
    query_today = UserEvent.objects.filter(audit_state='1',time__gte=today).values('event_type')\
                .annotate(sum=Count('*')).order_by()
#     print query,query_today
#     num_today = {'with_num_today':0,'ret_num_today':0,'coupon_num_today':0,'exc_num_today':0,}
#     num = {'with_num':0,'ret_num':0,'coupon_num':0,'exc_num':0}
    num_today = {'1':0,'2':0,'3':0,'4':0,'6':0}
    num = {'1':0,'2':0,'3':0,'4':0,'6':0}
    for q in query:
        index = q.get('event_type')
        num[index] = q.get('sum')
    for q in query_today:
        index = q.get('event_type')
        num_today[index] = q.get('sum')
#     print num,num_today
    total = {}
    dict1 = MyUser.objects.aggregate(cou=Count('id'), sumb=Sum('balance'),sums=Sum('scores'))
    total['user_num'] = dict1.get('cou')
    total['balance'] = (dict1.get('sumb') or 0)/100.0
    total['score'] = dict1.get('sums')
#     print TransList.objects.filter(user_event__event_type='2',user_event__audit_state='0').aggregate(cou=Count('id'),sum=Sum('transAmount'))
    dict_with = UserEvent.objects.filter(event_type='2',audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('translist__transAmount'))
    total['with_count'] = dict_with.get('cou')
    total['with_total'] = (dict_with.get('sum') or 0)/100.0

    dict_ret = UserEvent.objects.filter(event_type__in=['1','4','5','6','7'],audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('translist__transAmount'))
    total['ret_count'] = dict_ret.get('cou')
    total['ret_total'] = (dict_ret.get('sum') or 0)/100.0

    dict_coupon = UserEvent.objects.filter(event_type='4',audit_state='0').\
            aggregate(sum=Sum('translist__transAmount'))
    total['coupon_total'] = (dict_coupon.get('sum') or 0)/100.0

    dict_score = UserEvent.objects.filter(event_type='3',audit_state='0').\
            aggregate(sum=Sum('score_translist__transAmount'))
    total['ret_count'] = (dict_ret.get('cou') or 0)
    total['score_exchange_total'] = dict_score.get('sum')
    return render(request,"admin_index.html",{'num':num,'num_today':num_today,'total':total})

def get_admin_index_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_index')
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
    item_list = DayStatis.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
        item_list = item_list.filter(date__range=(s,e))

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
        i = {"date":con.date,
             "new_reg_num":con.new_reg_num,
             "active_num":con.active_num,
             "with_amount":con.with_amount/100.0,
             "with_num":con.with_num,
             "ret_amount":con.ret_amount/100.0,
             "ret_scores":con.ret_scores,
             "ret_num":con.ret_num,
             "coupon_amount":con.coupon_amount,
             "exchange_scores":con.exchange_scores,
             "lottery_people":con.lottery_people,
             "lottery_num":con.lottery_num,
             "envelope_people":con.envelope_people,
             "envelope_num":con.envelope_num,
             "envelope_money":con.envelope_money,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@transaction.atomic
def admin_finance(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_finance'))
        task_type = ContentType.objects.get_for_model(Finance)
        item_list = UserEvent.objects.filter(content_type = task_type.id, audit_state='1', time__lt=datetime.date.today()).values_list('object_id').distinct().order_by('object_id')
        project_list = ()
        for item in item_list:
            project_list += item
        projects = Finance.objects.filter(id__in=project_list)
        unaudited_pronames = []
        for project in projects:
            unaudited_pronames.append(project.title)
        return render(request,"admin_finance.html", {'unaudited_pronames':unaudited_pronames})
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_finance')
            return JsonResponse(res)
        if not admin_user.has_admin_perms('002'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        score = request.POST.get('score', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not event_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        event = UserEvent.objects.get(id=event_id)
        event_user = event.user
        card = event_user.user_bankcard.first()

        project = event.content_object   #jzy
        project_title = project.title   # jzy

        log = AuditLog(user=admin_user,item=event)
        translist = None
        scoretranslist = None
        if type==1:
            try:
                cash = float(cash)*100
                cash = int(cash)
                score = int(score)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0 or score < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if event.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if event.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                log.audit_result = True

                # translist = charge_money(event_user, '0', cash, u'福利返现')
                translist = charge_money(event_user, '0', cash, project_title)  #jzy
                if event.content_object.is_vip_bonus:
                    get_vip_bonus(event_user, cash, 'finance')
                scoretranslist = charge_score(event_user, '0', score, u'福利返现（积分）')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    #更新投资记录表
                    Invest_Record.objects.create(invest_date=event.time,invest_company=event.content_object.company.name,
                                                 user_name=card.real_name if card else '',card_number=card.card_number if card else '',
                                                 invest_mobile=event.invest_account,invest_period=event.invest_term,
                                                 invest_amount=event.invest_amount,return_amount=cash/100.0,wafuli_account=event_user.mobile,
                                                 return_date=datetime.date.today(),remark=event.remark)
                    msg_content = u'您提交的"' + event.content_object.title + u'"理财福利已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
                else:
                    res['code'] = -4
                    res['res_msg'] = "注意，重复提交时只提交失败项目，成功的可以输入0。\n"
                    if not translist:
                        logger.error(u"Charging cash is failed!!!")
                        res['res_msg'] += u"现金记账失败，请检查输入合法性后再次提交！"
                    if not scoretranslist:
                        logger.error(u"Charging score is failed!!!")
                        res['res_msg'] += u"积分记账失败，请检查输入合法性后再次提交！"
        else:
            event.audit_state = '2'
            log.audit_result = False
            log.reason = reason
            res['code'] = 0

            msg_content = u'您提交的"' + event.content_object.title + u'"理财福利审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");


        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='1')
            if translist:
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
            if scoretranslist:
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
            log.admin_item = admin_event
            log.save()
            event.audit_time = log.time
            event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)

@transaction.atomic
def admin_task(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_task'))
        return render(request,"admin_task.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_task')
            return JsonResponse(res)
        if not admin_user.has_admin_perms('002'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        score = request.POST.get('score', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not event_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        event = UserEvent.objects.get(id=event_id)
        event_user = event.user

        project = event.content_object   #jzy
        project_title = project.title   # jzy

        log = AuditLog(user=admin_user,item=event)
        translist = None
        scoretranslist = None
        if type==1:
            try:
                cash = float(cash)*100
                cash = int(cash)
                score = int(score)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0 or score < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if event.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if event.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                log.audit_result = True
                # translist = charge_money(event_user, '0', cash, u'福利返现')
                translist = charge_money(event_user, '0', cash, project_title)  #jzy
                if event.content_object.is_vip_bonus:
                    get_vip_bonus(event_user, cash, 'task')
                scoretranslist = charge_score(event_user, '0', score, u'福利返现（积分）')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    msg_content = u'您提交的"' + event.content_object.title + u'"体验福利已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
                else:
                    res['code'] = -4
                    res['res_msg'] = "注意，重复提交时只提交失败项目，成功的可以输入0。\n"
                    if not translist:
                        logger.error(u"Charging cash is failed!!!")
                        res['res_msg'] += u"现金记账失败，请检查输入合法性后再次提交！"
                    if not scoretranslist:
                        logger.error(u"Charging score is failed!!!")
                        res['res_msg'] += u"积分记账失败，请检查输入合法性后再次提交！"
        else:
            event.audit_state = '2'
            log.audit_result = False
            log.reason = reason
            task = event.content_object
            task.left_num = F("left_num")+1
            task.save(update_fields=['left_num'])
            res['code'] = 0

            msg_content = u'您提交的"' + event.content_object.title + u'"体验福利审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");

        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='1')
            if translist:
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
            if scoretranslist:
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
            log.admin_item = admin_event
            log.save()
            event.audit_time = log.time
            event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)

def get_admin_finance_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_finance')
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

    item_list = UserEvent.objects
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
        item_list = item_list.filter(finance__company__name__contains=companyname)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(finance__title__contains=projectname)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)

    task_type = ContentType.objects.get_for_model(Finance)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(event_type='1', audit_state=state).select_related('user')
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
def export_finance_excel(request):
    user = request.user
    item_list = []
    item_list = UserEvent.objects
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
        item_list = item_list.filter(finance__company__name__contains=companyname)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(finance__title__contains=projectname)
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    task_type = ContentType.objects.get_for_model(Finance)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(event_type='1', audit_state=state).select_related('user').order_by('time')
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
        item_list = item_list.filter(admin_event__admin_user__username=adminname)
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
        adminname = u'无' if not con.admin_event else con.admin_event.admin_user.username
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
def import_finance_excel(request):
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
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
                        return_amount = float(cell.value)
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
                event = UserEvent.objects.get(id=id)
                if event.audit_state != '1' or event.translist.exists():
                    continue
                log = AuditLog(user=admin_user,item=event)
                event_user = event.user
                translist = None
                if result:
                    amount = int(row[3]*100)
                    log.audit_result = True
                    translist = charge_money(event_user, '0', amount, row[1])
                    if event.content_object.is_vip_bonus:
                        get_vip_bonus(event_user, amount, 'finance')
                    if translist:
                        event.audit_state = '0'
                        translist.user_event = event
                        translist.save(update_fields=['user_event'])
                        Invest_Record.objects.create(invest_date=event.time,invest_company=event.content_object.company.name,
                                                         user_name=event_user.zhifubao_name,zhifubao=event_user.zhifubao,
                                                         invest_mobile=event.invest_account,invest_period=event.invest_term,
                                                         invest_amount=event.invest_amount,return_amount=amount/100.0,wafuli_account=event_user.mobile,
                                                         return_date=datetime.date.today(),remark=event.remark)
                    else:
                        logger.error(u"Charging cash is failed!!!")
                        logger.error("UserEvent:" + str(id) + u" 现金记账失败，请检查原因！！！！")
                        continue
                else:
                    event.audit_state = '2'
                    log.audit_result = False
                    log.reason = reason
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='1')
                if translist:
                    translist.admin_event = admin_event
                    translist.save(update_fields=['admin_event'])
                log.admin_item = admin_event
                log.save()
                event.audit_time = log.time
                event.save(update_fields=['audit_state','audit_time'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)
def get_admin_task_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_task')
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

    item_list = UserEvent.objects
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

    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(task__company__name__contains=companyname)

    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(task__title__contains=projectname)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    task_type = ContentType.objects.get_for_model(Task)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(event_type='1', audit_state=state).select_related('user').order_by('time')

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
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "type":con.content_object.get_type(),
             "company":project.company.name if project.company else u"无",
             "project":project.title,
             "mobile_sub":con.invest_account,
             "remark_sub":con.remark,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "ret_amount":u'无' if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount/100.0,
             "score":u'无' if con.audit_state!='0' or not con.score_translist.exists() else con.score_translist.first().transAmount,
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@transaction.atomic
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
                pcash = float(pcash)*100
                pcash = int(pcash)
                mcash = float(mcash)*100
                mcash = int(mcash)
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
            if translist:
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, event_type='4')
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
                res['code'] = 0
            else:
                res['code'] = -4
                res['res_msg'] = "现金记账失败，请检查输入合法性后再次提交！"
        elif type == 2:
            pscore = request.POST.get('pscore', 0)
            mscore = request.POST.get('mscore', 0)
            if not pscore:
                pscore = 0
            if not mscore:
                mscore = 0
            reason = request.POST.get('reason', '')
            if not pscore and not mscore or pscore and mscore or not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            try:
                pscore = int(pscore)
                mscore = int(mscore)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if pscore < 0 or mscore < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)

            scoretranslist = None
            if pscore > 0:
                scoretranslist = charge_score(obj_user, '0', pscore, reason)
            elif mscore > 0:
                scoretranslist = charge_score(obj_user, '1', mscore, reason)
            if scoretranslist:
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason,event_type='5')
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
                res['code'] = 0
            else:
                res['code'] = -4
                res['res_msg'] = u"积分记账失败，请检查输入合法性后再次提交！"
        elif type == 3:
            obj_user.is_active = False
            obj_user.save(update_fields=['is_active'])
            auth_logout(request)
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"加黑")
            res['code'] = 0
        elif type == 4:
            obj_user.is_active = True
            obj_user.save(update_fields=['is_active'])
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"去黑")
            res['code'] = 0
        elif type == 5:
            qq_number = request.POST.get('qq_number', '')
            level = request.POST.get('level',u'无')
            Channel.objects.create(user=obj_user, qq_number=qq_number, level=level)
            obj_user.is_channel = True
            obj_user.inviter_id = 1
            obj_user.save(update_fields=['is_channel','inviter'])
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"新增渠道")
            res['code'] = 0
        elif type == 6:
            obj_user.channel.delete()
            obj_user.is_channel = False
            obj_user.save(update_fields=['is_channel'])
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"取消渠道")
            res['code'] = 0
        elif type == 7:
            level = request.POST.get('level')
            if level:
                obj_user.channel.level=level
                obj_user.channel.save(update_fields=['level'])
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"修改渠道等级")
                res['code'] = 0
            else:
                res['code'] = -6
                res['res_msg'] = u"没有channel"
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
def admin_withdraw(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_withdraw'))
        return render(request,"admin_withdraw.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('004'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not event_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        event_id = int(event_id)
        event = UserEvent.objects.get(id=event_id)
        if event.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        log = AuditLog(user=admin_user,item=event)
        admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event.user, event_type='2')
        if type==1:
            event.audit_state = '0'
            log.audit_result = True
            res['code'] = 0
            #用户首次提现成功，立即发放邀请人100积分和三个随机红包奖励
            inviter = event.user.inviter
            if inviter:
                if not UserEvent.objects.filter(user=event.user, event_type='2', audit_state='0').exists():
                    invite_award_scores = settings.AWARD_SCORES
                    inviter.invite_scores += invite_award_scores
                    translist = charge_score(inviter, '0', invite_award_scores, u"邀请奖励")
                    if translist:
                        logger.debug('Inviting Award scores is successfully payed!')
                        inviter.save(update_fields=['invite_scores'])
                        translist.user_event = event
                        translist.admin_event = admin_event
                        translist.save(update_fields=['user_event','admin_event'])
                    else:
                        logger.debug('Inviting Award scores is failed to pay!!!')
            trans_withdraw = event.translist.first()
            if trans_withdraw:
                amount = trans_withdraw.transAmount
                vip_judge(event.user, amount)
                trans_withdraw.admin_event = admin_event
                trans_withdraw.save(update_fields=['admin_event'])
            msg_content = u'您提现的' + str(event.invest_amount) + u'福币，已发放到您的银行卡中，请注意查收'
            Message.objects.create(user=event.user, content=msg_content, title=u"提现审核")

        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            event.audit_state = '2'
            log.reason = reason
            log.audit_result = False
            translist = charge_money(event.user, '0', event.invest_amount, u'冲账', reverse=True)
            if translist:
                translist.user_event = event
                translist.admin_event = admin_event
                translist.save(update_fields=['user_event','admin_event'])
                res['code'] = 0
                msg_content = u'您提现的' + str(event.invest_amount) + u'福币未审核成功，原因：' + reason
                Message.objects.create(user=event.user, content=msg_content, title=u"提现审核");
            else:
                logger.critical(u"Charging cash is failed!!!")
                res['code'] = -2
                res['res_msg'] = u"现金记账失败，请检查输入合法性后再次提交！"
                return JsonResponse(res)
        log.admin_item = admin_event
        log.save()
        event.audit_time = log.time
        event.save(update_fields=['audit_state','audit_time'])
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

    item_list = UserEvent.objects.filter(event_type='2', audit_state=state).select_related('user').order_by('time','invest_amount')
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

    usertype = request.GET.get("usertype",0)
    usertype= int(usertype)
    if usertype == 1:
        item_list = item_list.filter(user__is_channel=False)
    elif usertype == 2:
        item_list = item_list.filter(user__is_channel=True)
        chalevel = request.GET.get("chalevel","")
        if chalevel:
            item_list = item_list.filter(user__channel__level=chalevel)
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
             "usertype":u"普通用户" if not con.user.is_channel else u"渠道："+ con.user.channel.level,
             "balance":obj_user.balance/100.0,
             "bank":bank,
             "real_name":real_name,
             "card_number":card_number,
             "amount":con.invest_amount/100.0,
             "time":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
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
    item_list = UserEvent.objects.filter(event_type='2', audit_state=state).select_related('user').order_by('time','invest_amount')
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

    usertype = request.GET.get("usertype",0)
    usertype= int(usertype)
    if usertype == 1:
        item_list = item_list.filter(user__is_channel=False)
    elif usertype == 2:
        item_list = item_list.filter(user__is_channel=True)
        chalevel = request.GET.get("chalevel","")
        if chalevel:
            item_list = item_list.filter(user__channel__level=chalevel)
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
        user_mobile = obj_user.mobile if not obj_user.is_channel else obj_user.channel.qq_number
        user_type = u"普通用户" if not obj_user.is_channel else u"渠道："+ obj_user.channel.level
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
                event = UserEvent.objects.get(id=id)
                if event.audit_state != '1':
                    continue
                log = AuditLog(user=admin_user,item=event)
                event_user = event.user
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event.user, event_type='2')
                if result:
                    event.audit_state = '0'
                    log.audit_result = True
                    #用户首次提现成功，立即发放邀请人100积分和三个随机红包奖励
                    inviter = event_user.inviter
                    if inviter:
                        if not UserEvent.objects.filter(user=event.user, event_type='2', audit_state='0').exists():
                            invite_award_scores = settings.AWARD_SCORES
                            inviter.invite_scores += invite_award_scores
                            translist = charge_score(inviter, '0', invite_award_scores, u"邀请奖励")
                            if translist:
                                logger.debug('Inviting Award scores is successfully payed!')
                                inviter.save(update_fields=['invite_scores'])
                                translist.user_event = event
                                translist.admin_event = admin_event
                                translist.save(update_fields=['user_event','admin_event'])
                            else:
                                logger.debug('Inviting Award scores is failed to pay!!!')
                    trans_withdraw = event.translist.first()
                    if trans_withdraw:
                        amount = trans_withdraw.transAmount
                        vip_judge(event.user, amount)
                        trans_withdraw.admin_event = admin_event
                        trans_withdraw.save(update_fields=['admin_event'])
                    msg_content = u'您提现的' + str(event.invest_amount) + u'福币，已发放到您的银行卡中，请注意查收'
                    Message.objects.create(user=event.user, content=msg_content, title=u"提现审核")

                else:
                    if not reason:
                        raise Exception(u"拒绝原因缺失")
                    event.audit_state = '2'
                    log.reason = reason
                    log.audit_result = False
                    translist = charge_money(event.user, '0', event.invest_amount, u'冲账', reverse=True)
                    if translist:
                        translist.user_event = event
                        translist.admin_event = admin_event
                        translist.save(update_fields=['user_event','admin_event'])
                        msg_content = u'您提现的' + str(event.invest_amount) + u'福币未审核成功，原因：' + reason
                        Message.objects.create(user=event.user, content=msg_content, title=u"提现审核");
                    else:
                        logger.critical(u"Charging cash is failed!!!")
                        raise Exception(u"记账失败")
                log.admin_item = admin_event
                log.save()
                event.audit_time = log.time
                event.save(update_fields=['audit_state','audit_time'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)

@transaction.atomic
def admin_score(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_score'))
        return render(request,"admin_score.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('003'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not event_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        event_id = int(event_id)
        event = UserEvent.objects.get(id=event_id)
        log = AuditLog(user=admin_user,item=event)
        if event.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if type==1:
            event.audit_state = '0'
            log.audit_result = True
            res['code'] = 0
            msg_content = u'您已成功兑换' + event.content_object.commodity.name + u'，消耗积分' + str(event.invest_amount)
            Message.objects.create(user=event.user, content=msg_content, title=u"积分兑换");
        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            event.audit_state = '2'
            log.reason = reason
            log.audit_result = False
            scoretranslist = charge_score(event.user, '0', event.invest_amount, u'冲账')
            if scoretranslist:
                scoretranslist.user_event = event
                scoretranslist.save(update_fields=['user_event'])
                res['code'] = 0
                msg_content = u'您兑换的' + event.content_object.commodity.name + u'未成功，原因：' + reason
                Message.objects.create(user=event.user, content=msg_content, title=u"积分兑换");
            else:
                logger.critical(u"Charging score is failed!!!")
                res['code'] = -2
                res['res_msg'] = u"现金记账失败，请检查输入合法性后再次提交！"
                return JsonResponse(res)
        admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event.user, event_type='8')
        log.admin_item = admin_event
        log.save()
        event.audit_time = log.time
        event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)
def get_admin_score_page(request):
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
    item_list = []
    item_list = UserEvent.objects
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

    commodityname = request.GET.get("commodityname", None)
    if commodityname:
        item_list = item_list.filter(exchangerecord__commodity__name__contains=commodityname)

    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    item_list = item_list.filter(event_type='3', audit_state=state).select_related('user').order_by('time')
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
        exchange_record = con.content_object
        commodity = exchange_record.commodity
        i = {"username":obj_user.username,
             "mobile":obj_user.mobile,
             "title":commodity.name,
             "price":commodity.price,
             "score":obj_user.scores,
             "id":con.id,
             "order_id":exchange_record.tranlist.id,
             "amount":con.invest_amount,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "remark":u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

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
        item_list = item_list.filter(admin_event__admin_user__username=adminname)

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
             "admin_user":u'无' if not con.admin_event else con.admin_event.admin_user.username,
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

@transaction.atomic
def admin_media(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_media'))
        return render(request,"admin_medialist.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_medialist')
            return JsonResponse(res)
        if not admin_user.has_admin_perms('002'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        score = request.POST.get('score', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not event_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        event = UserEvent.objects.get(id=event_id)
        event_user = event.user

        project = event.content_object   #jzy
        project_title = project.title   # jzy

        log = AuditLog(user=admin_user,item=event)
        translist = None
        scoretranslist = None
        if type==1:
            try:
                cash = float(cash)*100
                cash = int(cash)
                score = int(score)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0 or score < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if event.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if event.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                log.audit_result = True
                # translist = charge_money(event_user, '0', cash, u'福利返现')
                translist = charge_money(event_user, '0', cash, project_title)  #jzy
                if event.content_object.is_vip_bonus:
                    get_vip_bonus(event_user, cash, 'finance')
                scoretranslist = charge_score(event_user, '0', score, u'福利返现（积分）')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    msg_content = u'您提交的"' + event.content_object.title + u'"媒体单已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"媒体单审核");
                else:
                    res['code'] = -4
                    res['res_msg'] = "注意，重复提交时只提交失败项目，成功的可以输入0。\n"
                    if not translist:
                        logger.error(u"Charging cash is failed!!!")
                        res['res_msg'] += u"现金记账失败，请检查输入合法性后再次提交！"
                    if not scoretranslist:
                        logger.error(u"Charging score is failed!!!")
                        res['res_msg'] += u"积分记账失败，请检查输入合法性后再次提交！"
        else:
            event.audit_state = '2'
            log.audit_result = False
            log.reason = reason
            res['code'] = 0

            msg_content = u'您提交的"' + event.content_object.title + u'"媒体单审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"媒体单审核");

        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='11')
            if translist:
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
            if scoretranslist:
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
            log.admin_item = admin_event
            log.save()
            event.audit_time = log.time
            event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)

@login_required
@has_permission('002')
def export_media_excel(request):
    user = request.user
    item_list = []
    item_list = UserEvent.objects
    startTime = request.GET.get("investtime_0", None)
    endTime = request.GET.get("investtime_1", None)
    startTime2 = request.GET.get("audittime_0", None)
    endTime2 = request.GET.get("audittime_1", None)
    state = request.GET.get("audit_state",'1')
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
    mobile = request.GET.get("invest_account", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

    projectname = request.GET.get("project_title_contains", None)
    if projectname:
        item_list = item_list.filter(mediaproject__title__contains=projectname)
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    item_list = item_list.filter(event_type='9', audit_state=state).select_related('user').order_by('time')
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
#     sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=待审核记录.xls'
#     response.write(sio.getvalue())
    return response

@csrf_exempt
@has_permission('002')
def import_media_excel(request):
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
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
                        return_amount = float(cell.value)
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
                event = UserEvent.objects.get(id=id)
                if event.audit_state != '1' or event.translist.exists():
                    continue
                log = AuditLog(user=admin_user,item=event)
                event_user = event.user
                translist = None
                if result:
                    amount = int(row[3]*100)
                    log.audit_result = True
                    translist = charge_money(event_user, '0', amount, row[1])
                    if event.content_object.is_vip_bonus:
                        get_vip_bonus(event_user, amount, 'finance')
                    if translist:
                        event.audit_state = '0'
                        translist.user_event = event
                        translist.save(update_fields=['user_event'])
                        Invest_Record.objects.create(invest_date=event.time,invest_company=row[1],
                                                         user_name=event_user.zhifubao_name,zhifubao=event_user.zhifubao,
                                                         invest_mobile=event.invest_account,invest_period=event.invest_term,
                                                         invest_amount=event.invest_amount,return_amount=amount/100.0,wafuli_account=event_user.mobile,
                                                         return_date=datetime.date.today(),remark=event.remark)
                    else:
                        logger.error(u"Charging cash is failed!!!")
                        logger.error("UserEvent:" + str(id) + u" 现金记账失败，请检查原因！！！！")
                        continue
                else:
                    event.audit_state = '2'
                    log.audit_result = False
                    log.reason = reason
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='11')
                if translist:
                    translist.admin_event = admin_event
                    translist.save(update_fields=['admin_event'])
                log.admin_item = admin_event
                log.save()
                event.audit_time = log.time
                event.save(update_fields=['audit_state','audit_time'])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        logger.error(e)
        ret['code'] = 1
        ret['msg'] = unicode(e)
    ret['num'] = suc_num
    return JsonResponse(ret)