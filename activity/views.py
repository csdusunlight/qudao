#coding:utf-8
from django.shortcuts import render
from activity.models import IPLog, IPAward
from account.tools import get_client_ip
from django.db import transaction
from account.transaction import charge_money
from decimal import Decimal

# Create your views here.


def on_submit(request, user, investlog):
    ip = get_client_ip(request)
    IPLog.objects.create(user=user, investlog=investlog, ip=ip)
    
    
def on_audit_pass(request, investlog):
    if not hasattr(investlog, 'iplog'):
        return
    iplog = investlog.iplog
    ip = iplog.ip
    date = iplog.time.date()
    if IPAward.objects.filter(ip=ip,date=date).count() < 2:
        invest_amount = investlog.invest_amount
        if invest_amount < 10000:
            award = Decimal('1.88')
        else:
            award = Decimal('3.88')
        with transaction.atomic():
            charge_money(investlog.user, '0', award, u"活动奖励")
            IPAward.objects.create(ip=ip, date=date)
            iplog.award = award
            iplog.save(update_fields=['award',])
    