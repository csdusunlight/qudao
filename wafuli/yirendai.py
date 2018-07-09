#coding:utf-8
import datetime
import hashlib

import StringIO
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from xlwt import Workbook

from public.tools import is_staff
import logging
logger = logging.getLogger('wafuli')

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
order_url='https://tg.yirendai.com/promotion/notice/financeList'
user_url='https://tg.yirendai.com/promotion/notice/userList'
salt = b'~C):"vdX-SZz'

@csrf_exempt
def checkmobile(request):
    mobile = request.POST.get('mobile')
    start = request.POST.get('start')
    end = request.POST.get('end')
    if not start or not end:
        start = str(datetime.date.today())
        end = start

    params = dict(orgCode='huake', beginDate=start + ' 00:00:00', endDate=end + ' 23:59:59')
    response = requests.get(user_url, params=params, headers=headers)
    logger.info('yirendai'+response.text)
    data = response.json()
    user_data_list = data['data']

    cyptmobile = bytes(mobile.strip(),encoding='utf-8')
    cyptmobile = hashlib.md5(salt+mobile)
    for item in user_data_list:
        if item['mobile'] == cyptmobile:
            return JsonResponse({
                'code':0,
                'mobile': mobile.strip(),
                'createTime': item['createTime'],
                'source': item['source'],
            })
    return JsonResponse({'code':1})

@csrf_exempt
@is_staff
def export(request):
    start = request.POST.get('start')
    end = request.POST.get('end')
    if not start or not end:
        start = str(datetime.date.today())
        end = start
    params = dict(orgCode = 'huake',beginDate=start + ' 00:00:00',endDate= end + '23:59:59')
    response = requests.get(order_url, params=params, headers=headers)
    data = response.json()
    order_data_list = data['data']
    response = requests.get(user_url, params=params, headers=headers)
    data = response.json()
    user_data_list = data['data']
    w = Workbook()  # 创建一个工作簿
    ws = w.add_sheet(u'订单表')  # 创建一个工作表
    order_title_row = [u'是否为首单；1首单 0非首单', u'注册渠道', u'产品名称', u'手机号', u'投资金额', u'投资标期', u'购买时间', u'是否为新手标']
    for i in range(len(order_title_row)):
        ws.write(0, i, order_title_row[i])
    # style1 = easyxf(num_format_str='YY/MM/DD')
    for i, item in enumerate(order_data_list):
        data = [item['isNew'], item['source'], item['productName'], item['mobile'], item['investAmount'],
                item['closurePeriod'],
                item['sequestDate'], item['newUserProduct'], ]
        for j, d in enumerate(data):
            ws.write(i + 1, j, d)

    ws = w.add_sheet(u'注册表')  # 创建一个工作表
    user_title_row = [u'手机号', u'注册时间', u'注册来源',u'手机掩码']
    for i in range(len(user_title_row)):
        ws.write(0, i, user_title_row[i])
    # style1 = easyxf(num_format_str='YY/MM/DD')
    for i, item in enumerate(user_data_list):
        data = [item['mobile'], item['createTime'], item['source'], item['maskMobile']]
        for j, d in enumerate(data):
            ws.write(i + 1, j, d)

    sio = StringIO.StringIO()
    w.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=yirendai.xls'
    response.write(sio.getvalue())
