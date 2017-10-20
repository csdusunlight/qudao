#coding:utf-8
'''
Created on 2017年10月18日

@author: lch
'''
from public.tools import login_required_ajax, str_to_bool
from wafuli.models import Project, SubscribeShip
from django.http.response import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required_ajax
def create_update_selfproject(request, id=None):
    '''
            个人中心新建、编辑自建项目
    '''
    ret = {}
    user = request.user
    is_official = False
    title = request.POST.get('title', '')
    strategy = request.POST.get('strategy', '')
    introduction = request.POST.get('introduction', '')
    cprice = request.POST.get('cprice', '')
    shortprice = request.POST.get('shortprice', '')
    term = request.POST.get('term', '')
    investrange = request.POST.get('investrange', '')
    intrest = request.POST.get('intrest', '')
    is_multisub_allowed = request.POST.get('is_multisub_allowed', False)
    necessary_fields = request.POST.get('necessary_fields', '')
    marks = request.POST.get('marks', '')
    company = request.POST.get('company', '')
    if not (title and strategy and introduction and cprice and term and investrange and intrest
            and necessary_fields and company and shortprice):
        ret['code'] = 1
        ret['msg'] = u'缺少必填字段'
        return JsonResponse(ret)
    
    try:
        is_multisub_allowed = str_to_bool(is_multisub_allowed)
        marks = [ int(x) for x in marks.split(',') if x ]
    except:
        ret['code'] = 2
        ret['msg'] = u'字段不合法'
        return JsonResponse(ret)
    kwargs = {}
    if id is None:
        kwargs.update(user_id=user.id, title=title,strategy=strategy, introduction=introduction,
                               cprice=cprice, shortprice=shortprice, term=term,investrange=investrange, intrest=intrest,
                               is_multisub_allowed=is_multisub_allowed, necessary_fields=necessary_fields
                               ,company_id=company, state='10' )
    else:
        kwargs.update(title=title,strategy=strategy, introduction=introduction, shortprice=shortprice,
                        cprice=cprice, term=term,investrange=investrange, intrest=intrest,
                        is_multisub_allowed=is_multisub_allowed, necessary_fields=necessary_fields)
        
    with transaction.atomic():
        if id is None:
            obj = Project.objects.create(**kwargs)
            sub = SubscribeShip.objects.create(project=obj, user=user)
        else:
            Project.objects.filter(id=id).update(**kwargs)
            sub = SubscribeShip.objects.get(user=user, project_id=id)
        sub.marks = marks
    ret['code'] = 0
    return JsonResponse(ret)

def update_offiproject(request, id):
    ret = {}
    introduction = request.POST.get('introduction', '')
    price = request.POST.get('price', '')
    intrest = request.POST.get('intrest', '')
    marks = request.POST.get('marks', '')
    shortprice = request.POST.get('shortprice', '')
    if not (introduction and price and intrest and shortprice):
        ret['code'] = 1
        ret['msg'] = u'缺少必填字段'
        return JsonResponse(ret)
    
    try:
        marks = [ int(x) for x in marks.split(',') if x ]
    except:
        ret['code'] = 2
        ret['msg'] = u'字段不合法'
        return JsonResponse(ret)
    
    with transaction.atomic():
        sub = SubscribeShip.objects.get(id=id)
        sub.introduction=introduction
        sub.price=price
        sub.intrest=intrest
        sub.shortprice = shortprice
        sub.save(update_fields=['introduction','price','intrest','shortprice'])
        sub.marks = marks
    ret['code'] = 0
    return JsonResponse(ret)