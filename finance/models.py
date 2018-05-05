#coding:utf-8
from django.db import models
from django.utils import timezone

# Create your models here.
class ZhifubaoTransferLog(models.Model):
    payer_account = models.CharField(u"付款账号", max_length=30, blank=True)
    payee_account = models.CharField(u"收款账号", max_length=30)
    payee_real_name = models.CharField(u"收款姓名", max_length=20)
    amount = models.DecimalField(u"付款金额", decimal_places=2, max_digits=10)
    time = models.DateTimeField(u"付款时间", default=timezone.now)
    result = models.CharField(u"交易结果", max_length=50)
    def __unicode__(self):
        return u"结果：%s，时间：%s, 收款人：%s, 金额：%s" % (self.result, str(self.time), self.payee_real_name, str(self.amount))
    class Meta():
        ordering = ['-time',]
    