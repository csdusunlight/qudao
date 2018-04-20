#coding:utf-8
from django.db import models
from account.models import MyUser
from django.utils import timezone
from wafuli.models import Company, Project
from docs.models import Document
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.deletion import SET_NULL

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
    content_type = models.ForeignKey(ContentType,null=True,blank=True)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    auditlog = GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return u"%s:%s了%s现金 时间%s" % (self.user, self.get_transType_display(),self.transAmount, self.time)
    class Meta:
        ordering = ["-time", 'initAmount']
    
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
    user = models.ForeignKey(MyUser, related_name="margin_auditlog")
    type = models.CharField(max_length=2, choices=TRANS_TYPE, verbose_name=u"变动类型")
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    amount = models.DecimalField(u'数值', max_digits=10, decimal_places=2)
    admin_user = models.ForeignKey(MyUser, related_name="admin_margin_auditlog", null=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    audit_time = models.DateTimeField(u'审核时间', null=True, default=None)
    class Meta:
        ordering = ["-submit_time",]
    def __unicode__(self):
        return u"%s申请：%s, type:%s" % (self.user, self.amount, self.type)
    
    
class Apply_Project(models.Model):
    title = models.CharField(max_length=20, verbose_name=u"标题")
    submit_time = models.DateTimeField(u"申请时间", default=timezone.now)
    user = models.ForeignKey(MyUser, null=True, related_name="apply_projects")
    strategy = models.ForeignKey(Document, on_delete=SET_NULL, null=True)
    price = models.CharField(u"结算价格(给福利联盟的价格)",max_length=25, blank=True)
    promotion_price = models.CharField(u"放单价格（给渠道的价格）",max_length=25, blank=True)
    settle_period = models.CharField(u"结算周期", max_length=20)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    admin_user = models.ForeignKey(MyUser, related_name="admin_apply_project", null=True, default=None)
    audit_time = models.DateTimeField(u'审核时间', null=True, default=None)
    is_book = models.BooleanField(u"是否限量/需要预约", default=False)
    project = models.OneToOneField(Project, on_delete=SET_NULL, null=True)
    broker_rate = models.DecimalField(u"佣金比例，百分数", max_digits=10, decimal_places=2, default=0)
    invest_term = models.CharField(u"推广标期", max_length=20)
    invest_amount = models.CharField(u"推广档位", max_length=20)
    class Meta:
        verbose_name = u"放单申请"
        verbose_name_plural = u"放单申请"
        ordering = ["-submit_time",]
    def __unicode__(self):
        return self.title
    
    
class MerchantProjectStatistics(models.Model):
    project = models.OneToOneField(Project)
    submit_count = models.IntegerField(u"提交单数", default=0)
    settle_count = models.IntegerField(u"结算单数", default=0)
    appeal_count = models.IntegerField(u"申诉单数", default=0)
    abnormal_count = models.IntegerField(u"异常单数", default=0)
    toaudit_count = models.IntegerField(u"待处理单数", default=0)
    settle_amount = models.DecimalField(u'结算金额', max_digits=10, decimal_places=2)
    def view_count(self):
        return self.project.doc.view_count
    def __unicode__(self):
        return self.project.title