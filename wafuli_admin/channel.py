#coding:utf-8
'''
Created on 2017年3月27日

@author: lch
'''

import xlrd
from xlwt import *
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.http.response import JsonResponse, Http404
import traceback
from django.contrib.auth.decorators import login_required
from django.db import transaction
from wafuli.models import UserEvent, Finance
from account.models import DBlock, Channel, MyUser
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



def get_admin_channel_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_channel')
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

    item_list = Channel.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(join_time__range=(s,e))

    qq_number = request.GET.get("qq", None)
    if qq_number:
        item_list = item_list.filter(qq_number=qq_number)

    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)

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
        real_name = u'无'
        if con.user.user_bankcard.exists():
            card = con.user.user_bankcard.first()
            card_number = card.card_number
            real_name = card.real_name
        recent_login_time = u'无'
        if con.user.this_login_time:
            recent_login_time = con.user.this_login_time.strftime("%Y-%m-%d %H:%M")
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "card_number":card_number,
             "real_name":real_name,
             "join_time":con.join_time.strftime("%Y-%m-%d %H:%M"),
             'recent_login_time':recent_login_time,
             "balance":con.user.balance/100.0,
             "id":con.user.id,
             "qq":con.qq_number,
             'level':con.level
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
