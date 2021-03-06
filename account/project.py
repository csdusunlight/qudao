#coding:utf-8
'''
Created on 2017年10月18日

@author: lch
'''
from public.tools import login_required_ajax, str_to_bool
from wafuli.models import Project, SubscribeShip, Mark, Company
from django.http.response import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import random
from public.pinyin import PinYin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

@csrf_exempt
@login_required_ajax
def create_update_selfproject(request, id=None):
    '''
            个人中心新建、编辑自建项目
    '''
    if request.method == 'POST':
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
        is_book = request.POST.get('is_book', False)
        channel = request.POST.get('channel', '')
        up_price = request.POST.get('up_price', '')
        if not (title and strategy and cprice and term and investrange and intrest
                and necessary_fields and company and shortprice and is_book):
            ret['code'] = 1
            ret['msg'] = u'缺少必填字段'
            return JsonResponse(ret)
        
        try:
            is_multisub_allowed = str_to_bool(is_multisub_allowed)
            is_book = str_to_bool(is_book)
            marks = [ int(x) for x in marks.split(',') if x ]
        except:
            ret['code'] = 2
            ret['msg'] = u'字段不合法'
            return JsonResponse(ret)
        
        pyin = PinYin()
        pyin.load_word()
        szm, pinyin = pyin.hanzi2pinyin_split(title)
        kwargs = {}
        kwargs.update(szm=szm, pinyin=pinyin)
        if id is None:
            points = random.randint(5,50)
            kwargs.update(user_id=user.id, title=title,strategy=strategy, introduction=introduction,
                                   cprice=cprice, shortprice=shortprice, term=term,investrange=investrange, intrest=intrest,
                                   is_multisub_allowed=is_multisub_allowed, necessary_fields=necessary_fields
                                   ,company_id=company, state='10', points=points, is_book=is_book, channel=channel,
                                   up_price=up_price, category='self', is_official=False)
        else:
            kwargs.update(title=title,strategy=strategy, introduction=introduction, shortprice=shortprice,
                            cprice=cprice, term=term,investrange=investrange, intrest=intrest,
                            is_multisub_allowed=is_multisub_allowed, necessary_fields=necessary_fields, 
                            is_book=is_book, up_price=up_price,channel=channel,)
            
        with transaction.atomic():
            if id is None:
                obj = Project.objects.create(**kwargs)
                sub = SubscribeShip.objects.create(project=obj, user=user, price=cprice, shortprice=shortprice)
            else:
                Project.objects.filter(id=id, user=user).update(**kwargs)
                sub = SubscribeShip.objects.get(user=user, project_id=id)
                sub.price=cprice
                sub.shortprice=shortprice 
                sub.save(update_fields=['price','shortprice'])
            sub.marks = marks
        ret['code'] = 0
        return JsonResponse(ret)
    else:
        marks = Mark.objects.filter(user=request.user)
        kwargs = {'marks':marks}
        checked_marks = []
        if not id is None:
            id = int(id)
            kwargs.update(id=id)
            sub = get_object_or_404(SubscribeShip, project_id=id, user=request.user)
            checked_marks = [ int(x.id) for x in sub.marks.all() ]
        kwargs.update(checked_marks=checked_marks)
        companies = Company.objects.all()
        kwargs.update(companies=companies)
        template = 'account/m_personal_project.html' if request.mobile else 'account/personal_project.html'
        return render(request, template, kwargs)
    
@csrf_exempt    
@login_required
def update_offiproject(request, id):
    if request.method == 'POST':
        ret = {}
        introduction = request.POST.get('introduction', '')
        price = request.POST.get('price', '')
        intrest = request.POST.get('intrest', '')
        marks = request.POST.get('marks', '')
        shortprice = request.POST.get('shortprice', '')
        if not (price and intrest and shortprice):
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
    else:
        marks = Mark.objects.filter(user=request.user)
        kwargs = {'marks':marks}
        id = int(id)
        kwargs.update(id=id)
        sub = get_object_or_404(SubscribeShip, project_id=id, user=request.user)
        kwargs.update(subid = sub.id)
        checked_marks = [ int(x.id) for x in sub.marks.all() ]
        kwargs.update(checked_marks=checked_marks)
        template = 'account/m_official_project.html'
        return render(request, template, kwargs)

@csrf_exempt
@login_required_ajax
def delete_selfproject(request, id):
    ret = {}
    try:
        with transaction.atomic():
            project = Project.objects.get(id=id, user=request.user, is_official=False)
            project.state = '30'
            project.save(update_fields=['state'])
            SubscribeShip.objects.filter(project_id=id).delete()
            ret['code'] = 0
    except:
        ret['code'] = 1
        ret['msg'] = u"您没有权限"
    return JsonResponse(ret)