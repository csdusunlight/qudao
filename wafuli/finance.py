#coding:utf-8
from django.shortcuts import render
from django.http.response import Http404
from wafuli.models import Finance, Advertisement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import logging
from wafuli.tools import update_view_count
logger = logging.getLogger('wafuli')

def finance(request, id=None):
    if id is None:
        ad_list = Advertisement.objects.filter(location__in=['0','4'],is_hidden=False)[1:2]
        context = {'ad_list':ad_list}
        return render(request, 'finance.html',context)
    else:
        id = int(id)
        news = None
        try:
            news = Finance.objects.get(id=id)
        except Finance.DoesNotExist:
            raise Http404(u"该页面不存在")
        if not news.state in ["1", "2"]:
            raise Http404(u"该项目已下线")
        update_view_count(news)
        scheme = news.scheme
        table = []
        str_rows = scheme.split('|')
        for str_row in str_rows:
            row = str_row.split('#')
            table.append(row);
        other_wel_list = Finance.objects.filter(state='1', level__in=['normal','all']).order_by('-view_count')[0:10]
        context = {
                   'news':news,
                   'type':'Finance',
                   'other_wel_list':other_wel_list,
                   'table':table,
        }
        return render(request, 'detail-finance.html', context)

def add_finance(request, id=None):
    if id is None:
        ad_list = Advertisement.objects.filter(location__in=['0','4'],is_hidden=False)[0:1]
        context = {'ad_list':ad_list}
        return render(request, 'finance-add.html',context)
    else:
        id = int(id)
        news = None
        try:
            news = Finance.objects.get(id=id)
        except Finance.DoesNotExist:
            raise Http404(u"该页面不存在")
        if not news.state in ["1", "2"]:
            raise Http404(u"该项目已下线")
        update_view_count(news)
        scheme = news.scheme
        table = []
        str_rows = scheme.split('|')
        for str_row in str_rows:
            row = str_row.split('#')
            table.append(row);
        other_wel_list = Finance.objects.filter(state='1', level__in=['normal','all']).order_by('-view_count')[0:10]
        context = {
                   'news':news,
                   'type':'Finance',
                   'other_wel_list':other_wel_list,
                   'table':table,
        }
        return render(request, 'detail-finance.html', context)

def get_finance_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 8)
    company_background = request.GET.get("company_background", u'不限')
    invest_account = request.GET.get("invest_account", u'不限')
    project_type = request.GET.get("project_type", 0)
    project_status = request.GET.get("project_status", 0)


    try:
        size = int(size)
    except ValueError:
        size = 9
    if not page or size <= 0:
        raise Http404
    item_list = Finance.objects.filter(state__in=["1","2"], level__in=['normal','all'])

    # company_item = company_name.split('$')
    project_type = str(project_type)
    project_status = str(project_status)
    user = request.user
    # if user.is_authenticated() and user.is_channel:
    #     item_list = Finance.objects.filter(state__in=["1","2"])
    # else:
    #     item_list = Finance.objects.filter(state__in=["1","2"], level__in=['normal','all'])

    if company_background != u'不限':
        item_list = item_list.filter(background__contains=company_background)
    if invest_account != u'不限':
        item_list = item_list.filter(marks__name=invest_account)
    if project_type == '0':
        item_list = item_list.filter(f_type__in=["1","2"])
    else:
        item_list = item_list.filter(f_type=project_type)
    if project_status == '0':
        item_list = item_list.filter(state__in=["1","2"]).order_by("state","-priority", "-pub_date")
    else:
        item_list = item_list.filter(state=project_status)
        # now = datetime.now()
        # date = now-timedelta(days=100)
        # item_list = item_list.filter(pub_date__gte=date)

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
        marks = con.marks.all();
        str_marks = ''
        for mark in marks:
            str_marks += '<span>' + mark.name + '</span>'
        i = {"title":con.title,
             "interest":con.interest,
             "amount":con.amount_to_invest,
             "time":con.investTime,
             "revenue":con.revenue,
             "benefit":con.benefit,
             "url":con.url,
             "img_url":con.pic.url,
             "is_new":'new' if con.is_new() else '',
             "marks":str_marks,
             "end":'end' if con.state=='2' else ''
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
