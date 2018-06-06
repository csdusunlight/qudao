#coding:utf-8
from django.shortcuts import render
from public.tools import has_permission, has_post_permission
from wafuli.models import InvestLog
from django.http.response import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import F
import datetime
from account.transaction import charge_money
from django.db.models.aggregates import Sum, Count
from finance.pay import batch_transfer_to_zhifubao
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from xlwt.Workbook import Workbook
from xlwt.Style import easyxf
import StringIO,os
from django.views.decorators.csrf import csrf_exempt
import time
import xlrd
import traceback

# Create your views here.
@has_permission('200')
def finance_page(request):
    return render(request, 'finance_pay.html')
@csrf_exempt
@has_permission('200')
def check_transfer(request):
    user = request.user
    choices = request.POST.get('ids', '')
    if not choices:
        return JsonResponse({'code':1, 'detail':u'请勾选申请打款的记录'})
    id_list = choices.split(',')
    investlogs = InvestLog.objects.filter(id__in=id_list)
    count = 0
    total = Decimal(0)
    for investlog in investlogs:
        count += 1
        if investlog.return_amount > 0 and investlog.audit_state == '0' and \
               investlog.zhifubao and investlog.zhifubao_name and investlog.pay_state == '1':
            total += investlog.return_amount
        else:
            return JsonResponse({'code':3, 'detail':u"参数有误，请检查勾选项是否含有支付宝账号、姓名和返现金额，且状态为未打款"})
    if total > user.balance:
        return JsonResponse({'code':2, 'detail':u'您的账户余额不足（申请打款：%s元，您的余额：%s元）'\
                 % (str(total), str(user.balance))})
    ret_suc = {'code':0, 'total':total, 'count':count, 'balance':user.balance}
    return JsonResponse(ret_suc)

@csrf_exempt
@has_permission('200')
def submit_transfer(request):
    user = request.user
    choices = request.POST.get('ids', '')
    if not choices:
        return JsonResponse({'code':1, 'detail':u'请勾选申请打款的记录'})
    id_list = choices.split(',')
    investlogs = InvestLog.objects.filter(id__in=id_list)
    statis = investlogs.aggregate(total=Sum('return_amount'))
    if statis['total'] > user.balance:
        return JsonResponse({'code':2, 'detail':u'您的账户余额不足（申请打款：%s元，您的余额：%s元）'\
                 % (str(statis['total']), str(user.balance))})
    suc_num = 0
    fail_num = 0
    for investlog in investlogs:
        if investlog.return_amount > 0 and investlog.audit_state == '0' and \
               investlog.zhifubao and investlog.zhifubao_name and investlog.pay_state == '1':
            with transaction.atomic():
                charge_money(user, '1', investlog.return_amount, reason=u'给客户打款', auditlog=investlog)
                investlog.pay_state = '2'
                investlog.save(update_fields=['pay_state'])
            suc_num += 1
        else:
            fail_num += 1
    ret = {'code':0, 'suc_num':suc_num, 'fail_num':fail_num}
    return JsonResponse(ret)

@transaction.atomic
@has_post_permission('004')
def admin_autopay(request):
    admin_user = request.user
    if request.method == "GET":
        ret = {}
        paylist = InvestLog.objects.filter(is_official=True, audit_state='0', 
                                           pay_state='2', return_amount__lt=50000).all()
        sub_from = request.GET.get('sub_from')
        sub_to = request.GET.get('sub_to')
        if sub_from and sub_to:
            dateform = datetime.datetime.strptime(sub_from, '%Y-%m-%dT%H:%M')
            dateto = datetime.datetime.strptime(sub_to, '%Y-%m-%dT%H:%M')
            paylist = paylist.filter(submit_time__range=(dateform, dateto))
        id_list_str = request.GET.get('id_list')
        if id_list_str:
            id_list = [ int(x) for x in id_list_str.split(',') ]
            paylist = paylist.filter(id__in=id_list)
        dic = paylist.aggregate(count=Count('id'), sum=Sum('amount'))
        ret['count'] = dic['count'] or 0
        ret['sum'] = dic['sum'] or 0
        return JsonResponse(ret)
    if request.method == "POST":
        batch_list = []
        paylist = InvestLog.objects.filter(is_official=True, audit_state='0', 
                                           pay_state='2', return_amount__lt=50000).all()
        sub_from = request.POST.get('sub_from')
        sub_to = request.POST.get('sub_to')
        if sub_from and sub_to:
            dateform = datetime.datetime.strptime(sub_from, '%Y-%m-%dT%H:%M')
            dateto = datetime.datetime.strptime(sub_to, '%Y-%m-%dT%H:%M')
            paylist = paylist.filter(pay_apply_time__range=(dateform, dateto))
        id_list_str = request.POST.get('id_list')
        if id_list_str:
            id_list = [ int(x) for x in id_list_str.split(',') ]
            paylist = paylist.filter(id__in=id_list)
        for obj in paylist:
            batch_list.append({
                'obj': obj,
                'payee_account':obj.zhifubao,
                'payee_real_name':obj.zhifubao_name,
                'amount':str(obj.return_amount),
                'remark':obj.project.title
            })
        ret = batch_transfer_to_zhifubao(batch_list)
        fail_id_list = []
        for item in ret['detail']:
            obj = item['obj']
            fail_id_list.append(obj.id)
            obj.pay_reason = item['msg']
            obj.save(update_fields=['pay_reason'])
        paylist.exclude(id__in=fail_id_list).update(pay_state='3', pay_time=datetime.datetime.now())
        return JsonResponse({'suc_num':ret.get('suc_num')})

@login_required
@has_post_permission('004')
def admin_pay(request):
    admin_user = request.user
    if request.method == "GET":
        return render(request,"admin_pay.html")
    if request.method == "POST":
        res = {}
        investlog_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not investlog_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        investlog_id = int(investlog_id)
        investlog = InvestLog.objects.get(id=investlog_id)
        if investlog.pay_state != '2':
            res['code'] = -3
            res['res_msg'] = u'状态有误！'
            return JsonResponse(res)
        if type==1:
            investlog.pay_state = '3'
            res['code'] = 0
            withuser = investlog.user
            withuser.with_total = F('with_total')+investlog.return_amount
            withuser.save(update_fields=['with_total'])

        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            investlog.pay_state = '4'
            investlog.pay_reason = reason
            charge_money(investlog.user, '0', investlog.return_amount, u'冲账', True, reason, auditlog=investlog)
            res['code'] = 0
        investlog.pay_time = datetime.datetime.now()
        investlog.save(update_fields=['pay_state','pay_time','pay_reason'])
        return JsonResponse(res)
    
    
@login_required
def export_investlog_for_pay(request):
    user = request.user
    item_list = []
    item_list = InvestLog.objects.filter(user=user)
    investtime_0 = request.GET.get("investtime_0", None)
    investtime_1 = request.GET.get("investtime_1", None)
    submittime_0 = request.GET.get("submittime_0", None)
    submittime_1 = request.GET.get("submittime_1", None)
    audittime_0 = request.GET.get("auditdate_0", None)
    audittime_1 = request.GET.get("auditdate_1", None)
    state = request.GET.get("audit_state",'')
    pay_state = request.GET.get("pay_state",'')
    if submittime_0 and submittime_1:
        s = datetime.datetime.strptime(submittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(submittime_1,'%Y-%m-%d')
        e += datetime.timedelta(days=1)
        item_list = item_list.filter( submit_time__range=(s,e))
    if investtime_0 and investtime_1:
        s = datetime.datetime.strptime(investtime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(investtime_1,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    if audittime_0 and audittime_1:
        s = datetime.datetime.strptime(audittime_0,'%Y-%m-%d')
        e = datetime.datetime.strptime(audittime_1,'%Y-%m-%d')
        e += datetime.timedelta(days=1)
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
    if state:
        item_list = item_list.filter(audit_state=state)
    if pay_state:
        item_list = item_list.filter(pay_state=pay_state)
    item_list = item_list.select_related('project').order_by('-submit_time')
    data = []
    for con in item_list:
        project = con.project
        project_name=project.title
        invest_mobile=con.invest_mobile
        invest_name = con.invest_name
        invest_date=con.invest_date
        submit_date=con.submit_time.strftime("%Y-%m-%d")
        id=con.id
        remark= con.remark
        invest_amount= con.invest_amount
        term=con.invest_term
        qq_number = con.qq_number
        zhifubao = con.zhifubao
        zhifubao_name = con.zhifubao_name
        expect_amount = con.expect_amount
        user_level = con.user.level
        result = ''
        return_amount = ''
        settle_amount = ''
        reason = con.audit_reason
        if con.audit_state=='0':
            result = u'是'
            settle_amount = str(con.settle_amount)
            return_amount = str(con.return_amount)
        elif con.audit_state=='2':
            result = u'否'
        elif con.audit_state=='3':
            result = u'复审'
        data.append([id, project_name, submit_date, invest_date, invest_mobile, invest_name,invest_amount,
                     term, expect_amount, qq_number, remark, result, settle_amount, return_amount, zhifubao, zhifubao_name, reason])
    w = Workbook()     #创建一个工作簿
    ws = w.add_sheet(u'交单记录表')     #创建一个工作表
    title_row = [u'记录ID',u'项目名称',u'提交日期',u'投资日期', u'投资手机号', u'投资姓名',u'投资金额' ,u'投资标期', u'预期返现', u'QQ号',u'备注',
                 u'是否审核通过',u'结算金额',u'返现金额',u'支付宝账号', u'支付宝姓名',u'审核说明']
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

#用户返现数据导入
@csrf_exempt
@login_required
def import_investlog_for_pay(request):
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
    if ncols!=16:
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
                elif j==13:
                    return_amount = 0
                    if cell.value:
                        return_amount = Decimal(cell.value)
                    else:
                        raise Exception(u"返现金额不能为空。")
                    if return_amount == 0:
                        raise Exception(u"返现金额不能为零。")
                    temp.append(return_amount)
                elif j==14 or j==15:
                    result = cell.value.strip()
                    if result:
                        temp.append(result)
                    else:
                        raise Exception(u"支付宝账号和支付宝姓名不能为空。")
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
                InvestLog.return_amount = row[1]
                InvestLog.zhifubao = row[2]
                InvestLog.zhifubao_name = row[3]
                investlog = InvestLog.objects.filter(user=user).get(id=id)
                investlog.save(update_fields=['return_amount','zhifubao','zhifubao_name'])
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

@csrf_exempt
@has_permission('200')
def mark_pay_state(request):
    user = request.user
    state = request.POST.get('state', '')
    choices = request.POST.get('ids', '')
    if not state or not choices:
        return JsonResponse({'code':1, 'detail':u'参数不足'})
    id_list = choices.split(',')
    if state == '1' or state == '3':
        investlogs = InvestLog.objects.filter(user=user, id__in=id_list).exclude(state='2').update(pay_state=state)
    return JsonResponse({'code':0})
        
