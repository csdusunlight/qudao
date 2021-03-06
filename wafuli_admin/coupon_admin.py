#coding:utf-8
'''
Created on 2018年3月26日

@author: lch
'''

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import JsonResponse
from coupon.models import Contract, UserCoupon
from account.models import MyUser, Message
import logging
from account.varify import send_multimsg_bydhst
from public.tools import send_mobilemsg_multi
import datetime
logger = logging.getLogger('wafuli')
@csrf_exempt
@login_required
def deliver_coupon(request):
    admin_user = request.user
    if request.method == 'GET':
        return render(request, 'deliver_coupon.html')
    elif request.method == 'POST':
        result = {'code':0}
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            result['code'] = -4
            result['res_msg'] = u'请登录！'
            return JsonResponse(result)
        if not admin_user.has_admin_perms('010'):
            result['code'] = -5
            result['res_msg'] = u'您没有操作权限！'
            return JsonResponse(result)
        contract_id = request.POST.get('contract')
        contract_id_list = contract_id.split(',')
        contracts = Contract.objects.filter(id__in=contract_id_list)
        success_count = 0
        fail_list = []
        select_user = request.POST.get('selectuser')
        bulk_coupons = []
        bulk_msgs = []
        users = []
        user_set = set()
        if select_user == '1':
            users = list(MyUser.objects.all())
        elif select_user == '2':
            select_list_str = request.POST.get('users')
            select_list_str = str(select_list_str)
            select_list = select_list_str.strip().split('\n')
            users = MyUser.objects.filter(mobile__in = select_list)
        cnum = len(contracts)
        for user in users:
            for contract in contracts:
                if contract.start_date:
                    start_date = contract.start_date
                else:
                    start_date = datetime.date.today()
                end_date = start_date + datetime.timedelta(days=contract.continue_days)
                expire = start_date + datetime.timedelta(days=contract.exipire_days)
                coupon = UserCoupon(user=user, contract=contract, type='heyue', expire=expire,
                                    start_date=start_date, end_date=end_date, award=contract.award)
                bulk_coupons.append(coupon)
                success_count += 1
            user_set.add(user.mobile)
            msg = Message(user=user, title=u"红包提醒", content=u"您收到了%s个红包，快去个人中心-我的红包页面查看吧~" % str(cnum))
            user.num_message_sync += 1
            user.save(update_fields=['num_message_sync'])
            bulk_msgs.append(msg)
        if bulk_coupons:
            UserCoupon.objects.bulk_create(bulk_coupons)
        if bulk_msgs:
            Message.objects.bulk_create(bulk_msgs)
        send_mobilemsg_multi(user_set, u"您收到了新的推单红包，快去个人中心领取吧。联盟地址：%s" %  'http://fuliunion.com/account/hongbao/')

        result.update({'succ_num':success_count, 'fail_list':fail_list})
        return JsonResponse(result)

# def get_project_list(request):
#     if not request.is_ajax():
#         raise Http404
#     result={'prolist':{}}
#     type = request.GET.get('id', None)
#     if not type:
#         raise Http404
#     pro_list = CouponProject.objects.filter(ctype=str(type), state='1').only('id','title')
#     pro_dic={}
#     for x in pro_list:
#         pro_dic[str(x.id)] = x.title
#     result['prolist'] = pro_dic
#     return JsonResponse(result)
@csrf_exempt
def parse_file(request):
    res={'code':-9,}
    file = request.FILES.get('file')
    if not file:
        res['code'] = -2
        res['res_msg'] = u'请先选择文件！'
    else:
        try:
            res['list'] = handle_uploaded_file(file)
        except Exception, e:
            logger.info(e)
            res['code'] = -3
            res['res_msg'] = u'文件格式有误！'
        else:
            res['code'] = 0

    return JsonResponse(res)

def handle_uploaded_file(f):
    ret = []
    for line in f:
        line = line.decode('gbk')
#             line = unicode(line, errors='ignore')
        ret.append(line.strip())
    return ret