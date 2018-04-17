#coding:utf-8
import datetime

from django.db import models, transaction
from account.models import MyUser
from wafuli.models import InvestLog
from django.db.models.aggregates import Count, Sum
from account.transaction import charge_money

# Create your models here.

class Contract(models.Model):
    name = models.CharField(u"合约名称", max_length=20, unique=True)
    start_date = models.DateField(u"开始时间")
    end_date = models.DateField(u"结束时间")
    settle_count = models.IntegerField(u"结算单数")
    settle_amount = models.DecimalField(u"结算金额", decimal_places=2, max_digits=10)
    award = models.DecimalField(u"奖励金额", default=0, decimal_places=2, max_digits=6)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u"合约"
        verbose_name_plural = u"合约"

COUPONTYPE = (
    ('guanzhu', u'关注公众号红包'),
    ('bangka', u'绑卡红包'),
    ('heyue', u'合约红包'),
    ('shoudan', u'首次交单'),
)
COUPONSTATE = (
    ('0', u'未解锁'),
    ('1', u'已解锁'),
    ('2', u'已领取'),
)
def thirty_day_later():
    return datetime.date.today() + datetime.timedelta(days=30)
class UserCoupon(models.Model):
    type = models.CharField(u"红包类型", choices=COUPONTYPE, max_length=10)
    user = models.ForeignKey(MyUser, null=True, related_name="usercoupons")
    contract = models.ForeignKey(Contract, null=True)
    state = models.CharField(u"红包状态", choices=COUPONSTATE, default='0', max_length=2)
    create_date = models.DateField(u"发放日期", default=datetime.date.today)
    expire = models.DateField(u"过期时间", default=thirty_day_later)
    award = models.DecimalField(u"奖励金额", default=0, decimal_places=2, max_digits=6)
    unlock_date = models.DateField(u"解锁日期", default=None, null=True, blank=True)
    def checklock(self):
        if self.state != '0':
            return True
        if self.type == 'heyue':
            count, amount = self.check_schedule()
            if count >= self.contract.settle_count and amount >= self.contract.settle_amount:
                self.state = '1'
        elif self.type == 'bangka':
            if self.user.user_bankcard.exists():
                self.state = '1'
        elif self.type == 'shoudan':
            if self.user.investlog_submit.filter(audit_state='0').exists():
                self.state = '1'
        elif self.type == 'guanzhu':
            if self.user.weixin_users.exists():
                self.state = '1'
        if self.state == '1':
            self.create_date = datetime.date.today()
            self.save(update_fields = ['create_date', 'state'])
            return True
        else:
            return False
    def check_schedule(self):
        if self.type != 'heyue':
            return None, None
        dic = self.user.investlog_submit.filter(submit_time__range=(self.contract.start_date,
                 self.contract.end_date + datetime.timedelta(days=1)), audit_state='0').\
                 aggregate(cou=Count('*'),sum=Sum('settle_amount'))
        count = dic.get('cou') or 0
        amount = dic.get('sum') or 0
        return count, amount
    def is_expired(self):
        return datetime.date.today() > self.expire
    def is_to_expired(self):
        return datetime.date.today() + datetime.timedelta(days=3) > self.expire
    def open(self):
        if not self.is_expired() and self.state == '1':
            with transaction.atomic():
                self.state = '2'
                charge_money(self.user, '0', self.award, u'领取红包')
                self.save(update_fields = ['state'])
    def __unicode__(self):
        return self.get_type_display() + ' ' + self.user.mobile
    class Meta:
        ordering = ['-create_date']
        verbose_name = u"用户红包"
        verbose_name_plural = u"用户红包"