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
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
import time
from decimal import Decimal
from datetime import timedelta
logger = logging.getLogger("wafuli")

@login_required
@csrf_exempt
def channel(request):
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
        if ncols!=7:
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
                    elif j==4:
                        try:
                            term = str(int(float(cell.value)))
                        except Exception,e:
                            raise Exception(u"投资标期必须为数字，请修改后重新提交。")
                        temp.append(term)
                    elif j==3:
                        amount = cell.value
                        try:
                            amount = Decimal(amount)
                        except:
                            raise Exception(u"投资金额必须为数字")
                        temp.append(amount)
                    else:
                        value = cell.value
                        temp.append(value)
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
            db_key = DBlock.objects.select_for_update().get(index='investlog')
            if project.company is None:
                temp = InvestLog.objects.filter(project=project).exclude(audit_state='2').values('invest_mobile')
            else:
                temp = InvestLog.objects.filter(project__company_id=project.company_id).exclude(audit_state='2').values('invest_mobile')
            db_mobile_list = map(lambda x: x['invest_mobile'], temp)
            for i in range(len(mobile_list)):
                mob = mobile_list[i]
                if mob in db_mobile_list:
                    duplicate_mobile_list.append(mob)
                else:
                    item = rtable[i]
                    obj = InvestLog(user=request.user, invest_mobile=mob, project=project, is_official=project.is_official,is_selfsub=True,
                                    invest_amount=item[3],invest_term=item[4],invest_date=item[0],invest_name=item[2],
                                    audit_state='1',zhifubao=item[5],remark=item[6],submit_type='1')
                    log_list.append(obj)
            InvestLog.objects.bulk_create(log_list)
        succ_num = len(log_list)
        duplic_num1 = nrows - len(rtable)- 1
        duplic_num2 = len(rtable) - succ_num
        duplic_mobile_list_str = u'，'.join(duplicate_mobile_list)
        ret.update(code=0,sun=succ_num, dup1=duplic_num1, dup2=duplic_num2, anum=nrows-1, dupstr=duplic_mobile_list_str)
        return JsonResponse(ret)
    else:
        plist = list(Project.objects.filter(state__in=['10','20']).filter(Q(is_official=True)|Q(user=request.user)))    #jzy
        for p in plist:
            if not p.is_official:
                p.title = u"自建：" + p.title
        return render(request, 'account/account_submit.html', {'plist':plist})

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
        project = Project.objects.get(id=temp[0])
        time = datetime.datetime.strptime(temp[1],'%Y-%m-%d')
        invest_mobile = temp[2]
        amount = temp[3]
        term = temp[4]
        zhifubao = temp[5]
        invest_name = temp[6]
        remark = temp[7]
        submit_type = temp[8] or '1'
        try:
            if not project.is_multisub_allowed or submit_type=='1':
                if project.company is None:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
                else:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
                if queryset.exclude(audit_state='2').exists():
                    exist_num += 1   #jzy
                    exist_phone = exist_phone + project.title + invest_mobile + ";"   #jzy
                    raise ValueError('This invest_mobile is repective in project:' + str(project.id))
            InvestLog.objects.create(user=request.user, project=project, invest_date=time, invest_mobile=invest_mobile, invest_term=term,
                             invest_amount=Decimal(amount), audit_state='1', is_official=project.is_official, is_selfsub=True,
                             zhifubao=zhifubao, invest_name=invest_name, remark=remark, submit_type=submit_type,)
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

@login_required
def export_investlog(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects.filter(user=user)
    investtime_0 = request.GET.get("investtime_0", None)
    investtime_1 = request.GET.get("investtime_1", None)
    submittime_0 = request.GET.get("submittime_0", None)
    submittime_1 = request.GET.get("submittime_1", None)
    audittime_0 = request.GET.get("audittime_0", None)
    audittime_1 = request.GET.get("audittime_1", None)
    state = request.GET.get("audit_state",'')
    if not submittime_0 or not submittime_1:
        raise Http404
    s = datetime.datetime.strptime(submittime_0,'%Y-%m-%d')
    e = datetime.datetime.strptime(submittime_1,'%Y-%m-%d')
    if (e - s).days > 5:
        raise Http404
    item_list = item_list.filter( submit_time__range=(s,e))
    if investtime_0 and investtime_1:
        s = datetime.datetime.strptime(investtime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(investtime_1,'%Y-%m-%d')
        e += timedelta(days=1)
        item_list = item_list.filter(invest_date__range=(s,e))
    if audittime_0 and audittime_1:
        s = datetime.datetime.strptime(audittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(audittime_1,'%Y-%m-%d')
        e += timedelta(days=1)
        item_list = item_list.filter(audit_time__range=(s,e))
    qq_number = request.GET.get("qq_number", None)
    if qq_number:
        item_list = item_list.filter(user__qq_number=qq_number)
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
    userlevel = request.GET.get("level",None)
    if userlevel:
        item_list = item_list.filter(user__level=userlevel)
    is_official = request.GET.get("is_official",None)
    if is_official == "true":
        item_list = item_list.filter(is_official=True)
    elif is_official == "false":
        item_list = item_list.filter(is_official=False)
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(project__company__name__contains=companyname)
    invest_mobile = request.GET.get("mobile_sub", None)
    if invest_mobile:
        item_list = item_list.filter(invest_mobile=invest_mobile)    
    projectname = request.GET.get("project_title_contains", None)
    if projectname:
        item_list = item_list.filter(project__title__contains=projectname)
    adminname = request.GET.get("admin_user", None)
    if adminname:
        item_list = item_list.filter(admin_user__username=adminname)
    zhifubao = request.GET.get("zhifubao", None)
    if zhifubao:
        item_list = item_list.filter(zhifubao__contains=zhifubao)
    if not state:
        item_list = item_list.filter(audit_state=state)
    item_list = item_list.select_related('project').order_by('submit_time')
    data = []
    for con in item_list:
        project = con.project
        project_name=project.title
        invest_mobile=con.invest_mobile
        invest_name = con.invest_name
        invest_date=con.invest_date
        submit_date=con.submit_time.strftime("%Y-%m-%d")
        id=con.id
        other_remark= con.get_other_and_remark()
        invest_amount= con.invest_amount
        term=con.invest_term
        qq_number = con.user.qq_number
        user_level = con.user.level
        result = ''
        return_amount = ''
        settle_amount = ''
        reason = ''
        if con.audit_state=='0':
            result = u'是'
            settle_amount = str(con.settle_amount)
            return_amount = str(con.return_amount)
        elif con.audit_state=='2':
            result = u'否'
            reason = con.audit_reason
        data.append([id, project_name, submit_date, invest_date, invest_mobile, invest_name,invest_amount,
                     term, other_remark, result, settle_amount, return_amount, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'待审核记录')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'提交日期',u'投资日期', u'投资手机号', u'投资姓名',u'投资金额' ,u'投资标期', u'备注及其他',
                 u'是否审核通过',u'结算金额',u'返现金额',u'拒绝原因']
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
@csrf_exempt
@login_required
def import_investlog(request):
    user = request.user
    ret = {'code':-1}
    file = request.FILES.get('file')
#     print file.name
    tempfile = './out' + str(int(time.time())) + '.xls'
    with open(tempfile, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    data = xlrd.open_workbook(tempfile)
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    if ncols!=12:
        ret['msg'] = u"文件格式与模板不符，请在导出的投资记录表中更新后将文件导入！"
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
                    settle_amount = 0
                    if cell.value:
                        settle_amount = Decimal(cell.value)
                    elif result:
                        raise Exception(u"审核结果为是时，结算金额不能为空或零。")
                    temp.append(settle_amount)
                elif j==11:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    elif result:
                        raise Exception(u"审核结果为是时，结算金额不能为空或零。")
                    temp.append(return_amount)
                elif j==12:
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
                reason = row[5]
                investlog = InvestLog.objects.filter(user=user).get(id=id)
                if not investlog.is_official:
                    if result:
                        investlog.audit_state = '0'
                        settle_amount = row[3]
                        return_amount = row[4]
                        investlog.settle_amount = settle_amount
                        investlog.return_amount = return_amount
                    else:
                        investlog.audit_state = '2'
                        investlog.audit_reason = reason
                    investlog.audit_time = datetime.datetime.now()
                    investlog.save(update_fields=['audit_state','audit_time','settle_amount','return_amount','audit_reason'])
                else:
                    investlog.return_amount = return_amount
                    investlog.save(update_fields=['return_amount',])
                suc_num += 1
        ret['code'] = 0
    except Exception as e:
        traceback.print_exc()
        ret['code'] = 1
        ret['msg'] = unicode(e)
    finally:
        os.remove(tempfile)
    ret['num'] = suc_num
    return JsonResponse(ret)