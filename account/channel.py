#coding:utf-8
'''
Created on 2017年3月30日

@author: lch
'''
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse, Http404
from wafuli.models import InvestLog, Project
from account.models import DBlock
from django.db import transaction
import traceback
import xlrd
import os
from dragon.settings import STATIC_DIR
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import StringIO
from xlwt.Style import easyxf
from xlwt.Workbook import Workbook
import logging
import datetime
from django.contrib.contenttypes.models import ContentType
logger = logging.getLogger("wafuli")

@login_required
@csrf_exempt
def channel(request):
    if not request.user.is_channel:
        raise Http404
    if request.method == 'POST':
        fid = request.POST.get('fid')
        ret = {'code':-1}
        file = request.FILES.get('userfile')
#         print file.name
        filename = os.path.join(STATIC_DIR, 'excel', request.user.mobile + '.xls').replace('\\','/')
        with open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        data = xlrd.open_workbook(filename)
        table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols
        if ncols!=5:
            ret['msg'] = u"文件格式与模板不符，请下载最新模板填写！"
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
                        if(cell.ctype!=3):
                            raise Exception(u"投资日期列格式错误，请修改后重新提交。")
                        else:
                            time = xlrd.xldate.xldate_as_datetime(cell.value, 0)
                            temp.append(time)
                    elif j==1:
                        try:
                            mobile = str(int(cell.value)).strip()
                        except Exception,e:
                            raise Exception(u"手机号必须是11位数字，请修改后重新提交。")
                        if len(mobile)==11:
                            temp.append(mobile)
                        else:
                            raise Exception(u"手机号必须是11位数字，请修改后重新提交。")
                        if mobile in mobile_list:
                            duplic = True
                            break;
                        else:
                            mobile_list.append(mobile)
                    elif j==2:
                        try:
                            term = str(int(float(cell.value)))
                        except Exception,e:
                            raise Exception(u"投资标期必须为数字，请修改后重新提交。")
                        temp.append(term)
                    elif j==3:
                        amount = cell.value
                        try:
                            if float(amount) == int(amount):
                                amount = int(amount)
                            else:
                                amount = float(amount)
                        except:
                            raise Exception(u"投资金额必须为数字")
                        temp.append(amount)
                    else:
                        remark = cell.value
                        temp.append(remark)
                if duplic:
                    duplic = False
                else:
                    rtable.append(temp)
        except Exception, e:
            logger.info(unicode(e))
#             traceback.print_exc()
            ret['msg'] = unicode(e)
            return JsonResponse(ret)
        fid = int(fid)
        project = Project.objects.get(id=fid)
        ####开始去重
        log_list = []
        duplicate_mobile_list = []
        with transaction.atomic():
            db_key = DBlock.objects.select_for_update().get(index='event_key')
            temp = InvestLog.objects.filter(event_type='1',project=project).exclude(audit_state='2').values('invest_mobile')
            db_mobile_list = map(lambda x: x['invest_mobile'], temp)
            for i in range(len(mobile_list)):
                mob = mobile_list[i]
                if mob in db_mobile_list:
                    duplicate_mobile_list.append(mob)
                else:
                    item = rtable[i]
                    obj = InvestLog(user=request.user, invest_mobile=mob, project=project,
                                    invest_amount=item[3],invest_term=item[2],invest_time=item[0],
                                    audit_state='1',remark=item[4])
                    log_list.append(obj)
            InvestLog.objects.bulk_create(log_list)
        succ_num = len(log_list)
        duplic_num1 = nrows - len(rtable)- 1
        duplic_num2 = len(rtable) - succ_num
        duplic_mobile_list_str = u'，'.join(duplicate_mobile_list)
        ret.update(code=0,sun=succ_num, dup1=duplic_num1, dup2=duplic_num2, anum=nrows-1, dupstr=duplic_mobile_list_str)
        return JsonResponse(ret)
    else:
        flist = list(Project.objects.filter(state='1', level__in=['channel','all']).order_by('title'))      #jzy
        return render(request, 'account/account_channel.html', {'flist':flist})

@login_required
def submit_itembyitem(request):
    ret = {}
    data = request.POST.get('data','')
    if not data:
        ret['code'] = 1
        ret['msg'] = u'参数缺失'
        return JsonResponse(ret)
    table = data.split('$')
    suc_num = 0
    exist_num = 0   #jzy
    exist_phone = ""   #jzy
    for row in table:
        temp = row.split('|')
        news = Project.objects.get(id=temp[0])
        time = datetime.datetime.strptime(temp[1],'%Y-%m-%d')
        telnum = temp[2]
        amount = temp[3]
        term = temp[4]
        zhifubao = temp[5]
        zhifubao_name = temp[6]
        remark = temp[7]
        try:
            if not news.is_multisub_allowed and news.investlogs.filter(invest_mobile=telnum).exclude(audit_state='2').exists():
                exist_num += 1   #jzy
                exist_phone = exist_phone + telnum + ", "   #jzy
                raise ValueError('This invest_mobile is repective in project:' + str(news.id))
            else:
                InvestLog.objects.create(user=request.user, project=news, invest_date=time, invest_mobile=telnum, invest_term=term,
                                 invest_amount=int(amount), audit_state='1', is_official=True,
                                 zhifubao=zhifubao, zhifubao_name=zhifubao_name, remark=remark,)
                suc_num += 1
        except Exception, e:
            logger.info(e)
    result = {'code':0, 'suc_num':suc_num, 'exist_num':exist_num, 'exist_phone':exist_phone}   #jzy
    return JsonResponse(result)

def revise_project(request):
    result={'code':-1, 'url':'', 'data':{}}
    if not request.is_ajax():
        raise Http404
    user = request.user
    if not user.is_authenticated():
        result['code'] = 1
        return JsonResponse(result)
    if request.method == 'POST':
        project_id = request.POST.get("project_id", '')
        invest_project = request.POST.get("invest_project", '')
        invest_time = request.POST.get("invest_time", '')
        invest_tel = request.POST.get("invest_tel", '')
        invest_days = request.POST.get("invest_days",'')
        invest_money = request.POST.get("invest_money", '')
        invest_remarks = request.POST.get("invest_remarks", '')
        etype = ContentType.objects.get_for_model(Project)
        news = Project.objects.get(id=invest_project)
        project_item = InvestLog.objects.filter(user=request.user, content_type = etype).get(id=project_id)
        project_item.content_object = news
        project_item.invest_time = invest_time
        project_item.invest_mobile = invest_tel
        project_item.invest_term = invest_days
        project_item.invest_amount = invest_money
        project_item.remark = invest_remarks
        project_item.save()
        result['code'] = 0
        # result['data'] = {'content_object':news, 'invest_time':invest_time, 'invest_mobile':invest_tel, 'invest_term':invest_days, 'invest_amount':invest_money, 'remark':invest_remarks}
        result['data'] = {'content_object':news.title, 'invest_time':invest_time, 'invest_mobile':invest_tel, 'invest_term':invest_days, 'invest_amount':invest_money, 'remark':invest_remarks}
    return JsonResponse(result)

def export_audit_result(request):
    user = request.user
    fid = request.GET.get("fid")
    if fid == '0':      #jzy
        project = Project.objects.all()
        item_list = InvestLog.objects.filter(user=user, project=Project).order_by("-time")
    else:
        project = Project.objects.get(id=fid)
        item_list = InvestLog.objects.filter(user=user, project=Project).order_by("-time")
    data = []
    for con in item_list:
        # project_name=Project.title
        project = con.content_object        #jzy
        project_name=project.title          #jzy

        mobile_sub=con.invest_mobile
        # time_sub=con.time
        time_sub=con.invest_time            #jzy
        id=con.id
        remark= con.remark
        invest_amount= con.invest_amount
        term=con.invest_term
        result = con.get_audit_state_display(),
        return_amount = '' if con.audit_state!='0' or not con.translist.exists() else str(con.translist.first().transAmount/100.0),
        reason = '' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
        data.append([id, project_name, time_sub, mobile_sub, term, invest_amount, remark, result, return_amount, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'投资日期', u'注册手机号' ,u'投资期限' ,u'投资金额', u'备注', u'审核结果',u'返现金额',u'拒绝原因']
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
    response['Content-Disposition'] = 'attachment; filename=审核结果.xls'
    response.write(sio.getvalue())

    return response
