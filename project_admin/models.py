#coding:utf-8
from django.db import models
from django.utils import timezone
from wafuli.data import AUDIT_STATE, BANK
import time,datetime
from django.db.models import F
# Create your models here.
PROJECT_STATE=(
    ('prepare', u"未开始"),
    ('start', u"正在进行"),
    ('pause', u"暂停"),
    ('finish', u"已结束"),
)
SETTLE_STATE=(
    ('advance', u"预付款"),
    ('later', u"后付款"),
    ('daily', u"日结"),
)
SOURCE=(
    ('site', u"网站"),
    ('channel', u"渠道"),
)
COOPWAYS=(
    ('cpa', 'cpa'),
    ('cpc', 'cpc'),
    ('cps', 'cps'),
    ('cpm', 'cpm'),
    ('other', '其他'),
)
class Platform(models.Model):
    name = models.CharField(u"平台名称", max_length=20)
    url = models.CharField(u"网站域名", max_length=100)
    def __unicode__(self):
        return self.name
class Contact(models.Model):
    platform = models.ForeignKey(Platform, verbose_name=u"合作平台", related_name='contacts')
    name = models.CharField(u"姓名", max_length=50)
    mobile = models.CharField(u"手机号", max_length=50)
    qq = models.CharField(u"QQ号", max_length=50)
    weixin = models.CharField(u"微信号", max_length=50)
    invoicecompany = models.CharField(u"开票公司", max_length=50)
    invoiceid = models.CharField(u"开票税号", max_length=50)
    address = models.CharField(u"联系地址", max_length=50)
    remark = models.CharField(u"备注", max_length=50)
    def __unicode__(self):
        return self.name
def get_today():
    return datetime.date.today()
class Project(models.Model):
    name = models.CharField(u"项目名称", max_length=50)
    platform = models.ForeignKey(Platform, verbose_name=u"甲方名称", related_name='projects')
    time = models.DateField(u"立项日期", default=get_today)
    contact = models.CharField(u"商务对接人", max_length=10)
    coopway = models.CharField(u"合作方式", max_length=10, choices=COOPWAYS)
    settleway = models.CharField(u"结算方式", max_length=10, choices=SETTLE_STATE)
    contract_company = models.CharField(u"签约公司", max_length=30)
    settle_detail = models.CharField(u"结算详情", max_length=30)
    state = models.CharField(u"项目状态", max_length=10, choices=PROJECT_STATE)
    settle = models.DecimalField(u"结算费用", max_digits=10, decimal_places=2, default=0)
    consume = models.DecimalField(u"消耗总额", max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(u"项目成本", max_digits=10, decimal_places=2, default=0)
    cost_explain = models.CharField(u"成本说明", max_length=100,blank=True)
    finish_time = models.DateField(u"结项日期", null=True)
    remark = models.CharField(u"备注", max_length=100,blank=True)
    def consume_minus_paid(self):
        return self.consume - self.settle
    topay_amount = property(consume_minus_paid)
#     return_amount = models.DecimalField(u"返现总额", max_digits=10, decimal_places=2, default=0)
    def paid_minus_cost(self):
        return self.settle-self.cost
    profit = property(paid_minus_cost)
    def __unicode__(self):
        return str(self.id) + ' ' + self.name
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        if self.state != 'finish':
            self.cost = self.settle
            self.finish_time = None
        else:
            if not self.finish_time:
                self.finish_time = datetime.date.today()
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    class Meta:
        ordering = ["-time"]
class ProjectInvestData(models.Model):
    project = models.ForeignKey(Project, verbose_name=u"项目", related_name='project_data')
    is_futou = models.BooleanField(u"是否复投", default=False)
    source = models.CharField(u"投资来源", choices=SOURCE, max_length=10)
    invest_mobile = models.CharField(u"投资手机号", max_length=11)
    invest_time = models.DateField(u"投资时间")
    invest_amount = models.DecimalField(u"投资金额", max_digits=10, decimal_places=2)
    invest_term = models.CharField(u"投资标期", max_length=13)
    settle_amount = models.DecimalField(u"结算金额", max_digits=10, decimal_places=2)
    return_amount = models.DecimalField(u"返现金额", max_digits=10, decimal_places=2, default=0)
    audit_time = models.DateTimeField(u"审核时间（二次导入时间）", null=True)
    state = models.CharField(u"审核状态", max_length=10, choices=AUDIT_STATE)
    remark = models.CharField(u"备注", max_length=100)
    def __unicode__(self):
        return self.project.name + self.invest_mobile
    def futou_des(self):
        return u"复投" if self.is_futou else u"首投"


class ProjectStatis(models.Model):
    project = models.ForeignKey(Project, verbose_name=u"项目", related_name='project_statis')
    channel_consume = models.DecimalField(u"渠道消耗", max_digits=10, decimal_places=2, default=0)
    channel_return = models.DecimalField(u"渠道返现金额", max_digits=10, decimal_places=2, default=0)
    site_consume = models.DecimalField(u"网站消耗", max_digits=10, decimal_places=2, default=0)
    site_return = models.DecimalField(u"网站返现金额", max_digits=10, decimal_places=2, default=0)
    def consume(self):
        return self.channel_consume + self.site_consume
    def ret(self):
        return self.channel_return + self.site_return
    def __unicode__(self):
        return str(self.project_id) + self.project.name
    class Meta:
        ordering = ["-project__time"]
class DayStatis(models.Model):
    date = models.DateField(u"日期", primary_key=True)
    start_num = models.IntegerField(u"正在进行的项目数")
    finish_num = models.IntegerField(u"已结项的项目数")
    invest_count = models.IntegerField(u"投资人数")
    ret_count = models.IntegerField(u"返现人数")
    invest_sum = models.DecimalField(u"投资金额", max_digits=10, decimal_places=2, null=True)
    consume_sum = models.DecimalField(u"消耗金额", max_digits=10, decimal_places=2, null=True)
    ret_invest_sum = models.DecimalField(u"返现投资金额", max_digits=10, decimal_places=2, null=True)
    ret_sum = models.DecimalField(u"返现费用", max_digits=10, decimal_places=2, null=True)
    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")
    class Meta:
        ordering = ['-date']

ACCOUNT_TYPE=(
    ('public', '公账'),
    ('private', '私账'),
    ('invest', '投资'),
    ('loan', '借款'),
    ('other', '其他'),
)
class Account(models.Model):
    time = models.DateTimeField(u"创建时间", auto_now_add=True)
    type = models.CharField(u"账户类型", max_length=10, choices=ACCOUNT_TYPE)
    name = models.CharField(u"账户名称", max_length=50)
    bankaccount = models.CharField(u"银行账号", max_length=40)
    bank = models.CharField(u'开户银行', max_length=10, choices=BANK)
    subbranch = models.CharField(u"开户支行", max_length=40)
    balance = models.DecimalField(u"余额", max_digits=10, decimal_places=2)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    def __unicode__(self):
        return self.name
BILL_TYPE = (
    ('income', '收入'),
    ('expend', '支出'),
)
BILL_SUBTYPE = (
    ('swrz', '商务入账'),
    ('nbzr', '内部转入'),
    ('qtsr', '其他收入'),
    ('nbzc', '内部转出'),
    ('wztx', '网站提现'),
    ('gzbx', '工资报销'),
    ('swfy', '税务费用'),
    ('swcz', '商务出账'),
    ('qtzc', '其他支出'),
)
class AccountBill(models.Model):
    time = models.DateTimeField(u"账单时间", default=timezone.now)
    account = models.ForeignKey(Account, verbose_name=u"账户", related_name='account_bills')
    type = models.CharField(max_length=6, choices=BILL_TYPE, verbose_name=u"账单类型")
    subtype = models.CharField(max_length=6, choices=BILL_SUBTYPE, verbose_name=u"支出/收入类型")
    target = models.CharField(u"交易对象", max_length=100)
    amount = models.DecimalField(u"交易余额", max_digits=10, decimal_places=2)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    def strftime(self):
        return self.time.strftime("%Y-%m-%d %H:%M")
    def __unicode__(self):
        return self.account + ' ' + self.get_type_display() + ' ' + str(self.amount)
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        if self.id:
            return
        else:
            if self.type == 'income':
                self.account.balance = F('balance') + self.amount
            elif self.type == 'expend':
                self.account.balance = F('balance') - self.amount
            self.account.save(update_fields=['balance'])
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    
class DayAccountStatic(models.Model):
    date = models.DateField(u"日期", primary_key=True)
    income = models.DecimalField(u"收入", max_digits=10, decimal_places=2, null=True)
    expenditure = models.DecimalField(u"收入", max_digits=10, decimal_places=2, null=True)
    balance = models.DecimalField(u"收入", max_digits=10, decimal_places=2)
    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")
