#coding:utf-8
from django.db import models
from DjangoUeditor.models import UEditorField
from account.models import MyUser
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import datetime
from django.core.urlresolvers import reverse
def get_today():
    return datetime.date.today()
AUDIT_STATE = (
    ('0', u'审核通过'),
    ('1', u'待审核'),
    ('2', u'审核未通过'),
)    
class Company(models.Model):
    name = models.CharField(u"平台名称(必填)",max_length=100,unique=True)
    pinyin = models.CharField(u"平台名称拼音（排序用）",max_length=100,default='')
    level = models.CharField(u"安全评级",max_length=100,blank=True)
    site = models.CharField(u"网站地址",max_length=100,blank=True)
    capital = models.CharField(u"注册资金",max_length=100,blank=True)
    address = models.CharField(u"所在地区",max_length=100,blank=True)
    launch_date = models.CharField(u"上线时间",max_length=100,blank=True)
    trusteeship = models.CharField(u"托管情况",max_length=100,blank=True)
    background = models.CharField(u"平台背景",max_length=100,blank=True)
    information = models.CharField(u"公司信息",max_length=200,blank=True)
    logo = models.FileField(u"网站logo（210*100）", upload_to='logo/%Y/%m/%d',default='')
    view_count = models.IntegerField(u"热门度（点击总量，系统自动更新）", default=0)
    priority = models.IntegerField(u"优先级", default=0)
    class Meta:
        ordering = ['pinyin']
        verbose_name_plural = u"商家"
        verbose_name = u"商家"
    def __unicode__(self):
        return self.name
class Base(models.Model):
    title = models.CharField(max_length=200, verbose_name=u"标题")
    priority = models.IntegerField(u"优先级",default=3)
    pub_date = models.DateTimeField(u"创建时间", default=timezone.now)
    view_count = models.IntegerField(u"浏览量", default=0)
    change_user = models.CharField(u"上次修改用户", max_length=200, blank=True)
    url = models.CharField(u"本页面地址",max_length=200)
    def is_new(self):
        now = datetime.datetime.now()
        days = (now-self.pub_date).days
        return days == 0
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.title


class Mark(models.Model):
    name = models.CharField(max_length=10, verbose_name=u"标签名", unique=True)
    inviter = models.ForeignKey('self', related_name = 'child_marks', verbose_name=u"父标签",
                                blank=True, null=True, on_delete=models.SET_NULL)
    def __unicode__(self):
        return self.name

Project_STATE = (
    ('00', u'即将开始'),
    ('10', u'正在进行'),
    ('20', u'已结束'),
    ('30', u'已删除'),
)
Project_TYPE = (
    ('1', u'新手投资'),
    ('2', u'稳健投资'),
    ('3', u'高收益区'),
)
class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name=u"标题")
    priority = models.IntegerField(u"优先级",default=3)
    pub_date = models.DateTimeField(u"创建时间", default=timezone.now)
    user = models.ForeignKey(MyUser, null=True, related_name="created_projects")
    is_official = models.BooleanField(u"是否官方项目")
    state = models.CharField(u"项目状态", max_length=2, choices=Project_STATE)
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）")
    strategy = models.URLField(u"攻略链接")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, verbose_name=u"合作平台")
    type = models.CharField(u"项目类别", max_length=1, choices=Project_TYPE)
    is_multisub_allowed = models.BooleanField(u"是否允许同一手机号多次提交", default=False)
    introduction = models.TextField(u"项目简介",max_length=100)
    price01 = models.CharField(u"一级代理价格",max_length=20)
    price02 = models.CharField(u"二级代理价格",max_length=20)
    price03 = models.CharField(u"三级代理价格",max_length=20)
    cprice = models.CharField(u"客户指导价",max_length=20)
    term = models.CharField(u"标期长度", max_length=20)
    investrange = models.CharField(u"投资额度区间", max_length=20)
    intrest = models.CharField(u"预期年化", max_length=10)
    marks = models.ManyToManyField(Mark, verbose_name=u'标签', related_name="project_set", blank=True)
    subscribers = models.ManyToManyField(MyUser, through='SubscribeShip')
    class Meta:
        verbose_name = u"理财项目"
        verbose_name_plural = u"理财项目"
        ordering = ["-priority", "-pub_date"]
    
    def is_expired(self):
        return self.state != '10'
    def is_new(self):
        now = datetime.datetime.now()
        days = (now-self.pub_date).days
        return days == 0
    def is_hot(self):
        return self.view_count > 1000
    def __unicode__(self):
        return self.title
    
class SubscribeShip(models.Model):
    user = models.ForeignKey(MyUser)
    project = models.ForeignKey(Project)
    introduction = models.CharField(u"项目简介",max_length=100)
    myprice = models.CharField(u"保留字段",max_length=20)
    price = models.CharField(u"客户价",max_length=50)
    is_on = models.BooleanField(u"是否在主页显示",default=True)
    is_recommend = models.BooleanField(u"是否放到推荐位置",default=False)
    intrest = models.CharField(u"预期年化", max_length=10)
    def __unicode__(self):
        return self.user.mobile + self.project.title
    class Meta:
        unique_together = (('user', 'project'),)

class InvestLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="investlog_submit")
    project = models.ForeignKey(Project, related_name="investlogs")
    is_official = models.BooleanField()
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    invest_mobile = models.CharField(u"投资手机号", max_length=11)
    invest_name = models.CharField(u"投资用户名", max_length=11, blank=True)
    invest_amount = models.DecimalField(u'投资金额', max_digits=10, decimal_places=2)
    invest_term = models.IntegerField(u"投资标期")
    invest_image = models.CharField(u"投资截图", max_length=1000, blank=True)
    invest_date = models.DateField(u'投资日期', default=get_today)
    qq_number = models.CharField(u"QQ号", max_length=20, blank=True)
    zhifubao = models.CharField(u'支付宝账号', max_length=64)
    zhifubao_name = models.CharField(u'支付宝姓名', max_length=30)
    admin_user = models.ForeignKey(MyUser, related_name="investlog_admin", null=True)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    audit_reason = models.CharField(u"审核原因", max_length=30, blank=True)
    settle_amount = models.DecimalField(u'结算金额', max_digits=10, decimal_places=2, default=0)
    return_amount = models.DecimalField(u'返现金额', max_digits=10, decimal_places=2, default=0)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    def __unicode__(self):
        return u"来自渠道用户：%s 的投资数据提交：%s" % (self.user, self.invest_amount)
    class Meta:
        ordering = ["-submit_time",]
    
class Notice(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_notice")
    content = models.CharField(u"通知内容", max_length=100)
    time = models.DateTimeField(u"创建时间", default=timezone.now)
    priority = models.IntegerField(u"优先级",default=1)
    def __unicode__(self):
        return self.content
    class Meta:
        verbose_name = u"个人主页最新公告"
        verbose_name_plural = u"个人主页最新公告"
        ordering = ['-priority', '-time']

ADMIN_TYPE = (
    ('1', u'更改现金余额'),
    ('2', u'更改用户状态'),
    ('3', u'更改用户等级'),
)   
class AdminLog(models.Model):
    admin_user = models.ForeignKey(MyUser, related_name="user_admin_history")
    custom_user = models.ForeignKey(MyUser, related_name="user_byadmin_history")
    type = models.CharField(max_length=2, choices=ADMIN_TYPE, verbose_name=u"管理员事件类型")
    time = models.DateTimeField(u'操作时间', auto_now_add=True)
    remark = models.CharField(u"备注", max_length=100)
    def __unicode__(self):
        return u"%s给%s做了%s操作,时间：%s" % (self.admin_user, self.custom_user, self.get_event_type_display(),
                                       self.time)
    class Meta:
        ordering = ["-time",]

TRANS_TYPE = (
    ('0', u'增加'),
    ('1', u'减少'),
)

class TransList(models.Model):
    user = models.ForeignKey(MyUser, related_name="translist")
    time = models.DateTimeField(u'时间', auto_now_add=True)
    initAmount = models.DecimalField(u'变动前数值', max_digits=10, decimal_places=2)
    transAmount = models.DecimalField(u'变动数值', max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, verbose_name=u"变动原因")
    remark = models.CharField(u"备注", max_length=100, blank=True)
    transType = models.CharField(max_length=2, choices=TRANS_TYPE, verbose_name=u"变动类型")
    investlog = models.ForeignKey(InvestLog, related_name="translist", null=True,on_delete=models.SET_NULL)
    adminlog = models.ForeignKey(AdminLog, related_name="translist", null=True,on_delete=models.SET_NULL)
    def __unicode__(self):
        return u"%s:%s了%s现金 提交时间%s" % (self.user, self.get_transType_display(),self.transAmount,
                                       self.user_event.time if self.user_event else "")
    class Meta:
        ordering = ["-time",]

class WithdrawLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="withdrawlog")
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    amount = models.DecimalField(u'提现数值', max_digits=10, decimal_places=2)
    admin_user = models.ForeignKey(MyUser, related_name="withdrawlog_admin", null=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    class Meta:
        ordering = ["submit_time",]
    def get_bank(self):
        return self.user.user_bankcard.first().bank
    def get_cardnumber(self):
        return self.user.user_bankcard.first().card_number
    def get_realname(self):
        return self.user.user_bankcard.first().real_name
    def __unicode__(self):
        return u"%s申请提现：%s" % (self.user, self.amount)
# class Press(Base):
#     summary = models.TextField(verbose_name=u"摘要")
#     type = models.CharField(u"新闻类型", max_length=1, choices=NEWS_TYPE)
#     pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True,
#                              verbose_name=u"新闻图片上传(110*72)")
#     content=UEditorField(u"内容", width=900, height=300, toolbars="full",
#                          imagePath="photos/%(year)s/%(month)s/%(day)s/",
#                          filePath="photos/%(year)s/%(month)s/%(day)s/",
#                          upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
#     #增加title、keywords、description等seo字段
#     seo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
#     seo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
#     seo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
#     def clean(self):
#         if self.type == '3' and not self.pic:
#             raise ValidationError({'pic': u'新闻类型必输'})
#     class Meta:
#         ordering = ["-priority","-pub_date"]
#         verbose_name = u"公告、攻略（关于我们）"
#         verbose_name_plural = u"公告、攻略（关于我们）"


ADLOCATION_NEW = (
    ('00', u'首页banner（1250*400）'),
#     ('01', u'首页推荐位（200*200），配不超过20字的文字描述'),
#     ('02', u'首页发现位（280*200），配不超过30字的文字描述'),
#     ('03', u'首页中间广告位（1250*110）'),
#     ('04', u'首页下面的广告位（870*110）'),
#     ('10', u'红包页大banner（680*380）'),
#     ('11', u'红包页小banner（275*185）'),
)
class MAdvert_PC(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"图片上传", help_text=u"保证图片质量的前提下，越小越好，莉萍负责图片 审核")
    location = models.URLField(u"位置", choices=ADLOCATION_NEW)
    description = models.CharField(u"文字描述", max_length=30, blank=True)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    class Meta:
        ordering = ["-priority","-pub_date"]
        verbose_name = u"PC端广告位（新）"
        verbose_name_plural = u"PC端广告位（新）"
    def clean(self):
        if self.pic:
            if self.location in ['00', '10', '03'] and self.pic.size > 100000:
                raise ValidationError({'pic': u'图片大小不能超过100k'})
            elif self.pic.size > 50000:
                raise ValidationError({'pic': u'图片大小不能超过50k'})

class Announcement(models.Model):
    content = models.CharField(u"通知内容", max_length=100)
    time = models.DateTimeField(u"创建时间", default=timezone.now)
    priority = models.IntegerField(u"优先级",default=1)
    def __unicode__(self):
        return self.content
    class Meta:
        verbose_name = u"个人中心的通知"
        verbose_name_plural = u"个人中心的通知"
        ordering = ['-priority', '-time']