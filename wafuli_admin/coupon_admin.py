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
from account.models import MyUser
import logging
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
        contract = Contract.objects.get(id=contract_id)
        success_count = 0
        fail_list = []
        select_user = request.POST.get('selectuser')
        award = request.POST.get('award')
        bulk = []
        users = []
        if select_user == '1':
            users = MyUser.objects.all()
            for user in users:
                coupon = UserCoupon(user=user, contract=contract, award=award, type='heyue', award=contract.award)
                bulk.append(coupon)
                success_count += 1
        elif select_user == '2':
            select_list_str = request.POST.get('users')
            select_list_str = str(select_list_str)
            select_list = select_list_str.strip().split('\n')
            user_set = set([])
            for user in select_list:
                if user:
                    user_set.add(user)
            for mobile in user_set:
                try:
                    user = MyUser.objects.get(mobile = mobile)
                    users.append(user)
                except:
                    fail_list.append(mobile)
                else:
                    coupon = UserCoupon(user=user, contract=contract, award=award, type='heyue', award=contract.award)
                    bulk.append(coupon)
                    success_count += 1
        if bulk:
            UserCoupon.objects.bulk_create(bulk)
            
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