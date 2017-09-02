#coding:utf-8
'''
Created on 20160617

@author: lch
'''

from django.shortcuts import render, redirect
from wafuli.models import UserEvent, AdminEvent, AuditLog, TransList, UserWelfare,\
    Message
import datetime
from django.db.models import Sum, Count
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money, charge_score
import logging
from account.models import MyUser
from wafuli_admin.models import RecommendRank
# Create your views here.
logger = logging.getLogger('wafuli')

def admin_recommend_return(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_recommend_return'))
        return render(request,"admin_recommend.html")
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
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_recommend_return')
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
                translist = charge_money(event_user, '0', cash, u'活动奖励')
                scoretranslist = charge_score(event_user, '0', score, u'活动奖励')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    
                    msg_content = u'您推荐的"' + event.content_object.title + u'"福利已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"福利推荐审核");
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
            
            msg_content = u'您推荐的"' + event.content_object.title + u'"福利审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"福利推荐审核");
        
        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='9')
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
            
def get_admin_recommend_return_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_recommend_return')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
#     projecttype = request.GET.get("projecttype",'0')
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
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    item_list = item_list.filter(event_type='6', audit_state=state).select_related('user')
    
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
        customer = con.user
        try:
            rankInfo = RecommendRank.objects.get(user=customer)
        except:
            acc_num = 0
            rank = '--'
        else:
            acc_num = rankInfo.acc_num
            rank = rankInfo.rank
        today = datetime.date.today() 
        first_day = datetime.datetime(today.year, today.month, 1)
        rej_num = UserEvent.objects.filter(user=customer, event_type='6', \
                        time__gte=first_day, audit_state='2').count()
        wel = con.content_object
#         project = con.content_object
#         if projecttype=='2' and not isinstance(project, Finance):
#             continue
#         elif projecttype=='1' and not isinstance(project, Task):
#             continue
        i = {"username":customer.username,
             "acc_num":acc_num,
             "rej_num":rej_num,
             "rank":rank,
             "title":wel.title,
             "url":wel.url,
             "reason":wel.reason,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "amount":u'无' if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount,
             "score":u'无' if con.audit_state!='0' or not con.score_translist.exists() else con.score_translist.first().transAmount,
             "id":con.id,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)