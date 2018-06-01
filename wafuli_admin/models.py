#coding:utf-8
from django.db import models
from account.models import MyUser
from django.utils import timezone
from wafuli.data import AUDIT_STATE
from decimal import Decimal
import datetime
class DayStatis(models.Model):
    date = models.DateField(u"日期", primary_key=True)
    apply_num = models.PositiveIntegerField(u"新申请人数", default=0)
    refuse_num = models.PositiveIntegerField(u"新拒绝人数", default=0)
    new_reg_num = models.PositiveIntegerField(u"新成功注册人数", default=0)
    with_amount = models.IntegerField(u'提现成功金额', default=0)
    with_num = models.PositiveIntegerField(u"提现成功人数", default=0)
    ret_amount = models.DecimalField(u'返现金额', default=0, max_digits=10, decimal_places=2)
    admin_amount = models.DecimalField(u'管理员添加金额', default=0, max_digits=10, decimal_places=2)
    coupon_amount = models.DecimalField(u'红包金额', default=0, max_digits=10, decimal_places=2)
    invest_amount = models.PositiveIntegerField(u"投资金额", default=0)
    ret_num = models.PositiveIntegerField(u"返现人数", default=0)
    new_project_num = models.PositiveIntegerField(u"今日上线项目数", default=0)
    activity_consume = models.DecimalField(u'账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    merchant_people = models.IntegerField(u'商家人数', default=0)
    merchant_people_active = models.IntegerField(u'放单商家人数', default=0)
    merchant_projects = models.IntegerField(u'在线项目数量', default=0)
    merchant_investlogs_submit = models.IntegerField(u'商家项目交单数量', default=0)
    merchant_investlogs_audit = models.IntegerField(u'交单审核通过数量', default=0)
    merchant_charge = models.DecimalField(u'保证金充值', default = Decimal(0), max_digits=10, decimal_places=2)
    merchant_consume = models.DecimalField(u'保证金消耗', default = Decimal(0), max_digits=10, decimal_places=2)
    merchant_broker = models.DecimalField(u'佣金', default = Decimal(0), max_digits=10, decimal_places=2)
    merchant_settle = models.DecimalField(u'结算金额', default = Decimal(0), max_digits=10, decimal_places=2)
    coupon_total = models.IntegerField(u'发放红包数量', default=0)
    coupon_user_total = models.IntegerField(u"发放红包用户数", default=0)
    coupon_award = models.DecimalField(u'红包奖励金额', default = Decimal(0), max_digits=10, decimal_places=2)
    coupon_total_unlock = models.IntegerField(u'激活红包数量', default=0)
    coupon_user_total_unlock = models.IntegerField(u"激活红包用户数", default=0)
    coupon_award_unlock = models.DecimalField(u'激活红包奖励金额', default = Decimal(0), max_digits=10, decimal_places=2)
    
    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")
    class Meta:
        ordering = ['-date']


class GlobalStatis(models.Model):
    time = models.DateTimeField(u"统计时间", auto_now=True)
    invest_total = models.PositiveIntegerField(u"累计奖励金额", default=0)
    with_total = models.PositiveIntegerField(u'累计提现金额', default=0)
    user_total = models.PositiveIntegerField(u'累计加入渠道数量', default=0)
    invite_total = models.PositiveIntegerField(u'累计渠道引入用户', default=0)
    all_wel_num = models.PositiveIntegerField(u"累计上线项目", default=0) 

class Dict(models.Model):
    key = models.CharField(max_length=20,primary_key=True)
    value = models.CharField(max_length=512)
    expire_stamp = models.IntegerField()
    def __unicode__(self):
        return self.key + ':' + self.value


class Invest_Record(models.Model):
    invest_date = models.DateField(u"创建时间", default=timezone.now)
    invest_company = models.CharField(max_length=20)
    qq_number = models.CharField(max_length=15)
    user_name = models.CharField(max_length=20)
    zhifubao = models.CharField(max_length=50)
    card_number = models.CharField(max_length=50)
    invest_mobile = models.CharField(max_length=11)
    invest_period = models.CharField(max_length=10)
    invest_amount = models.IntegerField()
    return_amount = models.IntegerField()
    wafuli_account = models.CharField(max_length=11)
    return_date = models.DateField(u"创建时间", default=timezone.now)
    is_futou = models.BooleanField(u"是否复投", default=False)
    coupon = models.CharField(u"优惠券", max_length=100,blank=True)
    remark = models.CharField(u"备注", max_length=100,blank=True)

class Message_Record(models.Model):
    time = models.DateField(u"群发时间", default=timezone.now)
    msgid = models.CharField(u"批次号",max_length=32)
    content = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural = u"短信群发记录"
        verbose_name = u"短信群发记录"
        
    
