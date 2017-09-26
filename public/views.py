#coding:utf-8
from django.shortcuts import render
from wafuli.models import InvestLog
from django.contrib.auth.decorators import login_required
import datetime
from xlwt.Workbook import Workbook
from xlwt.Style import easyxf
import StringIO
from django.http.response import HttpResponse

# Create your views here.
@login_required
def export_invest_excel(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects
    if not user.is_staff:
        item_list = item_list.filter(user=user)
    investtime_0 = request.GET.get("investtime_0", None)
    investtime_1 = request.GET.get("investtime_1", None)
    submittime_0 = request.GET.get("submittime_0", None)
    submittime_1 = request.GET.get("submittime_1", None)
    audittime_0 = request.GET.get("audittime_0", None)
    audittime_1 = request.GET.get("audittime_1", None)
    state = request.GET.get("audit_state",'1')
    if investtime_0 and investtime_1:
        s = datetime.datetime.strptime(investtime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(investtime_1,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    if submittime_0 and submittime_1:
        s = datetime.datetime.strptime(submittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(submittime_1,'%Y-%m-%d')
        item_list = item_list.filter(submit_time__range=(s,e))
    if audittime_0 and audittime_1:
        s = datetime.datetime.strptime(audittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(audittime_1,'%Y-%m-%d')
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
    if is_official:
        item_list = item_list.filter(is_official=is_official)
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
    item_list = item_list.filter(audit_state=state).select_related('user', 'project').order_by('submit_time')
    data = []
    for con in item_list:
        project = con.project
        project_name=project.title
        invest_mobile=con.invest_mobile
        invest_date=con.invest_date
        id=con.id
        remark= con.remark
        invest_amount= con.invest_amount
        term=con.invest_term
        qq_number = con.user.qq_number
        user_level = con.user.level
        result = ''
        return_amount = ''
        reason = ''
        if con.audit_state=='0':
            result = u'是'
            return_amount = str(con.settle_amount)
        elif con.audit_state=='2':
            result = u'否'
            reason = con.audit_reason
        data.append([id, project_name, invest_date, qq_number,user_level, invest_mobile, term,
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