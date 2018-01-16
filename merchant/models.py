#coding:utf-8
from django.db import models
from account.models import MyUser
from django.utils import timezone

# Create your models here.
TRANS_TYPE = (
    ('0', u'增加'),
    ('1', u'减少'),
)
class Margin_Translog(models.Model):
    user = models.ForeignKey(MyUser, related_name="translog")
    time = models.DateTimeField(u'时间', auto_now_add=True)
    initAmount = models.DecimalField(u'变动前数值', max_digits=10, decimal_places=2)
    transAmount = models.DecimalField(u'变动数值', max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, verbose_name=u"变动原因")
    remark = models.CharField(u"备注", max_length=100, blank=True)
    transType = models.CharField(max_length=2, choices=TRANS_TYPE, verbose_name=u"变动类型")
    def __unicode__(self):
        return u"%s:%s了%s现金 时间%s" % (self.user, self.get_transType_display(),self.transAmount, self.time)
    class Meta:
        ordering = ["-time",]
    
    def balance(self):
        if self.transType == '0':
            return self.initAmount + self.transAmount
        else:
            return self.initAmount - self.transAmount
        
AUDIT_STATE = (
    ('0', u'审核通过'),
    ('1', u'待审核'),
    ('2', u'审核未通过'),
)    
class Margin_AuditLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="margin_withdrawlog")
    type = models.CharField(max_length=2, choices=TRANS_TYPE, verbose_name=u"变动类型")
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    amount = models.DecimalField(u'数值', max_digits=10, decimal_places=2)
    admin_user = models.ForeignKey(MyUser, related_name="withdrawlog_admin", null=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    class Meta:
        ordering = ["submit_time",]
    def __unicode__(self):
        return u"%s申请：%s, type:%s" % (self.user, self.amount, type)