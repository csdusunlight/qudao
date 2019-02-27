import time
import traceback

import os
import xlrd
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from account.varify import sendmsg_bydhst
from wafuli_admin.models import Message_Log
from weixin.tasks import send_msgs


@csrf_exempt
@login_required
def import_msg_excel(request):
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
    if ncols!=2:
        ret['msg'] = u"文件格式必须有两列，手机号和短信内容"
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
                    mobile = str(cell.value)
                    temp.append(mobile)
                elif j==1:
                    content = cell.value
                    temp.append(content)
            rtable.append(temp)
    except Exception, e:
        traceback.print_exc()
        ret['msg'] = unicode(e)
        ret['num'] = 0
        return JsonResponse(ret)
    # send_msgs.delay(rtable)
    ret['num'] = len(rtable)
    return JsonResponse(ret)