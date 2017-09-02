#coding:utf-8
from django.db import models
from DjangoUeditor.models import UEditorField
from account.models import MyUser
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import OneToOneField
from .data import *
from django.template.defaultfilters import default
from django.utils import timezone
import datetime
from django.core.urlresolvers import reverse
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
    class Meta:
        ordering = ['pinyin']
        verbose_name_plural = u"商家"
        verbose_name = u"商家"
    def __unicode__(self):
        return self.name
class Base(models.Model):
    title = models.CharField(max_length=200, verbose_name=u"标题")
    news_priority = models.IntegerField(u"优先级",default=3)
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
class News(Base):
    state = models.CharField(u"项目状态", max_length=1, choices=STATE)
#     is_futou = models.BooleanField(u'是否允许复投（重复提交同一手机号）', default= False)
    is_vip_bonus = models.BooleanField(u'适用VIP奖励', default=True)
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）")
    isonMobile = models.BooleanField(u'是否只限移动端（pc端显示二维码）？', default= False)
    exp_url_pc = models.CharField(u"活动地址pc", blank=True, max_length=200)
    exp_url_mobile = models.CharField(u"活动地址mobile", blank=True, max_length=200)
    exp_code = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, verbose_name=u"上传二维码")
#     advert = models.ForeignKey("Advertisement",blank=True, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    #增加title、keywords、description等seo字段
    seo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
    seo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
    seo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
    class Meta:
        abstract = True
    def clean(self):
        if self.isonMobile == False and self.exp_url_pc == '':
                raise ValidationError({'exp_url_pc': u'请输入活动体验地址'})
        if self.isonMobile and self.exp_code == '':
            raise ValidationError({'exp_code': u'请上传二维码'})
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
    def is_expired(self):
        return self.state == '2' or self.state == '3'
class ZeroPrice(News):
    provider = models.CharField(u"商家", max_length=10)
    time_limit = models.CharField(u"活动时间", max_length=24)
    zero_type = models.CharField(max_length=1, choices=ZERO_TYPE, verbose_name=u"福利类型")
    strategy=UEditorField(u"活动内容", width=900, height=600, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    class Meta:
        verbose_name = u"免费福利"
        verbose_name_plural = u"免费福利"
        ordering = ["-news_priority", "-pub_date"]
class Mark(models.Model):
    name = models.CharField(max_length=10, verbose_name=u"标签名", unique=True)
    inviter = models.ForeignKey('self', related_name = 'child_marks', verbose_name=u"父标签",
                                blank=True, null=True, on_delete=models.SET_NULL)
    def __unicode__(self):
        return self.name
class Welfare(Base):
    type = models.CharField(max_length=10, choices=WELFARE_TYPE, editable=False, verbose_name=u"福利类型")
    is_display = models.BooleanField(default=True, verbose_name=u"是否在免费福利中显示")
    marks = models.ManyToManyField(Mark, verbose_name=u'标签', related_name="welfare_set", blank=True)
    state = models.CharField(u"项目状态", max_length=1, choices=STATE)
    startTime = models.DateTimeField(u"生效时间（粒度为小时）", default=timezone.now)
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）",blank=False)
    company = models.ForeignKey(Company)
    provider = models.CharField(u"商家", max_length=10)
    seo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
    seo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
    seo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
    time_limit = models.CharField(u"活动时间", max_length=24)
    strategy=UEditorField(u"活动内容", width=900, height=600, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
#     advert = models.ForeignKey("Advertisement",blank=True, null=True, on_delete=models.SET_NULL)
    isonMobile = models.BooleanField(u'是否只限移动端（pc端显示二维码）？', default= False)
#     exp_url = models.CharField(u"活动地址（已废弃）", blank=True, max_length=200)
    exp_url_pc = models.CharField(u"活动地址pc", blank=True, max_length=200)
    exp_url_mobile = models.CharField(u"活动地址mobile", blank=True, max_length=200)
    exp_code = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, verbose_name=u"上传二维码")
    def clean(self):
        if self.exp_url_mobile == '':
                raise ValidationError({'exp_url_mobile': u'请输入活动体验地址'})
        if self.isonMobile == False and self.exp_url_pc == '':
                raise ValidationError({'exp_url_pc': u'请输入活动体验地址'})
        if self.isonMobile and self.exp_code == '':
            raise ValidationError({'exp_code': u'请上传二维码'})
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
    def is_expired(self):
        return self.state == '2' or self.state == '3'
    class Meta:
        ordering = ["-news_priority", "-startTime"]
    def is_new(self):
        now = datetime.datetime.now()
        days = (now-self.startTime).days
        return days == 0
    def is_hot(self):
        return self.view_count > 1000
    def get_type(self):
        return u"免费福利"
    def get_type_url(self):
        return reverse('welfare')
HTYPE = (
    ('0', u'微信红包'),
    ('1', u'支付宝红包'),
    ('2', u'购物红包'),
    ('3', u'话费红包'),
    ('4', u'流量红包'),
    ('5', u'理财红包'),
)
class Hongbao(Welfare):
    htype = models.CharField(u"红包类型", max_length=1, choices=HTYPE)
    subtitle = models.CharField(u"副标题", max_length=20, blank=False)
    is_qualified = models.BooleanField(u"精选", default=False)
    up = models.IntegerField(u"顶", default=0)
    down = models.IntegerField(u"踩", default=0)
    class Meta:
        verbose_name = u"红包"
        verbose_name_plural = u"红包"
        ordering = ["-up",]
class Baoyou(Welfare):
    mprice = models.CharField(u"市场价", max_length=10)
    nprice = models.CharField(u"现价", max_length=10)
    desc = models.CharField(u"描述", max_length=20)
    class Meta:
        verbose_name = u"9.9包邮"
        verbose_name_plural = u"9.9包邮"
class CouponProject(Welfare):
    ctype = models.CharField(max_length=1, choices=COUPON_TYPE, verbose_name=u"优惠券类型")
    amount =models.CharField(u'金额(xx元或x%)', max_length=10)
    is_vip_bonus = models.BooleanField(u'适用VIP奖励', default=True)
    endtime = models.DateField(u"截止日期")
    introduction = models.TextField(u"使用说明",max_length=200)
    claim_limit = models.SmallIntegerField(u"限领次数", default=1)
    def __unicode__(self):
        return '%s:%s' % (self.get_ctype_display(), self.title)
    class Meta:
        ordering = ['-pub_date']
        verbose_name = u"优惠券项目"
        verbose_name_plural = u"优惠券项目"
class Coupon(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_coupons", null=True)
    project = models.ForeignKey(CouponProject, related_name="coupons")
    time = models.DateField(u"领取或发放日期", default=timezone.now)
    exchange_code = models.CharField(u"兑换码", blank=True, max_length=50)
    is_used = models.BooleanField(u"是否已使用", default = False)
    user_event = GenericRelation("UserEvent",related_query_name='coupon')
    def __unicode__(self):
        return self.project.title
    class Meta:
        verbose_name = u"优惠券"
        verbose_name_plural = u"优惠券"
#         ordering = ['-time']
#     def clean(self):
#         if self.type == '2' and self.exchange_code == '':
#             raise ValidationError({'exchange_code': u'使用券的兑换码是必输项'})
    def is_to_expired(self):
        endTime = self.project.endtime
        today = datetime.date.today()
        dif = (endTime-today).days
        return dif <= 7 and dif >= 0
    def is_expired(self):
        endTime = self.project.endtime
        today = datetime.date.today()
        return endTime < today
class Task(News):
    type = models.CharField(max_length=10, choices=TASK_TYPE, verbose_name=u"任务类型")
    is_forbidden = models.BooleanField(u"禁止用户领取（暂停任务）", default=False)
    left_num = models.IntegerField(u"剩余数量")
    moneyToAdd = models.IntegerField(u"奖励福币")
    scoreToAdd = models.IntegerField(u"奖励积分",default=0)
    provider = models.CharField(u"商家", max_length=10)
    time_limit = models.CharField(u"活动时间", max_length=24)
    rules =UEditorField(u"奖励规则", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    strategy =UEditorField(u"体验步骤", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    user_event = GenericRelation("UserEvent",related_query_name='task')
    def get_type(self):
        return u"体验福利"
    def get_type_url(self):
        return reverse('task')
    class Meta:
        verbose_name = u"体验福利"
        verbose_name_plural = u"体验福利"
        ordering = ["-news_priority", "-pub_date"]
class Finance(News):
    level = models.CharField(u"项目级别", max_length=10, choices=FINANCE_LEVEL, default="normal")
    f_type = models.CharField(u"项目类别", max_length=1, choices=FINANCE_TYPE)
#     filter = models.CharField(u"项目系列", max_length=2, choices=FILTER)
    is_multisub_allowed = models.BooleanField(u"是否允许同一手机号多次提交", default=False)
    introduction = models.TextField(u"平台简介",max_length=200)     #jzy
    background = models.CharField(u"平台背景", max_length=20)
    regcap = models.CharField(u"注册资本", max_length=10)
    onlinedate = models.CharField(u"上线时间", max_length=12)
    depository = models.CharField(u"银行存管", max_length=10)
    ICP = models.CharField(u"ICP号", max_length=30)
    scheme = models.CharField(u"奖励方案",max_length=200,help_text="用‘#’分列，‘|’分行，只能包含4列，行数不限，示例：\
        1000元#10天#投资额*2%#25%|2000元#20天#投资额*3%#30%|...")
    marks = models.ManyToManyField(Mark, verbose_name=u'标签', related_name="finance_set", blank=True)
    revenue = models.CharField(u"综合年化收益", max_length=10)
    benefit = models.CharField(u"补贴收益", max_length=100)
    amount_to_invest = models.IntegerField(u"起投额度")
    investTime = models.CharField(u"标期长度", max_length=100)
    interest = models.CharField(u"官网利息",max_length=8)
    strategy =UEditorField(u"体验步骤", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    rules =UEditorField(u"注意事项", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    user_event = GenericRelation("UserEvent",related_query_name='finance')
    def get_type(self):
        return u"理财福利"
    def get_type_url(self):
        return reverse('finance')
    class Meta:
        verbose_name = u"理财福利"
        verbose_name_plural = u"理财福利"
        ordering = ["-news_priority", "-pub_date"]
class Commodity(models.Model):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"商品图片上传(190*165)")
    name = models.CharField(u"商品名称", max_length=100)
    price = models.IntegerField(u"价格")
    category = models.CharField(u"商品分类", max_length=8, choices=CATEGORY)
    item = models.CharField(u"商品子类", max_length=8, choices=ITEM)
    url = models.CharField(u"本页面地址",max_length=200)
#     advert = models.ForeignKey("Advertisement",blank=True, null=True, on_delete=models.SET_NULL)
    rules =UEditorField(u"奖品介绍", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    strategy =UEditorField(u"兑换流程", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u"商品"
        verbose_name_plural = u"积分商品"
class Message(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_msgs")
    title = models.CharField(u"标题", max_length=30, default=u"系统消息")
    time = models.DateTimeField(u"日期", default=timezone.now)
    is_read = models.BooleanField(u"是否已读", default=False)
    content = models.TextField(u"消息内容")
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = u"消息"
        verbose_name_plural = u"消息"
        ordering = ['-time']
class UserEvent(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_event_history")
#    event_level = models.PositiveIntegerField(u'事件级别（决定是否需审核）')
    event_type = models.CharField(max_length=10, choices=USER_EVENT_TYPE, verbose_name=u"用户事件类型")
    invest_account = models.CharField(u"第三方注册账号/提现账号", max_length=100)
    invest_amount = models.IntegerField(u'涉及金额', default=0)
    invest_term = models.CharField(u"投资标期", max_length=100)
    invest_image = models.CharField(u"投资截图", max_length=1000)
    invest_time = models.DateTimeField(u'投资时间', default=timezone.now)
    time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    remark = models.CharField(u"备注", max_length=100,blank=True)
    content_type = models.ForeignKey(ContentType,null=True,blank=True)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    def get_content_object(self):
        return self.content_object
    def __unicode__(self):
        return u"%s的用户事件：%s" % (self.user, self.get_event_type_display())
    class Meta:
        ordering = ["-time",]
class AdminEvent(models.Model):
    admin_user = models.ForeignKey(MyUser, related_name="user_admin_history")
    custom_user = models.ForeignKey(MyUser, related_name="user_awarding_history")
    event_type = models.CharField(max_length=10, choices=ADMIN_EVENT_TYPE, verbose_name=u"管理员事件类型")
    time = models.DateTimeField(u'操作时间', auto_now_add=True)
    remark = models.CharField(u"备注", max_length=100)
    def __unicode__(self):
        return u"%s给%s做了%s操作,时间：%s" % (self.admin_user, self.custom_user, self.get_event_type_display(),
                                       self.time)
    class Meta:
        ordering = ["-time",]

class AuditLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="audited_logs")
    item = models.ForeignKey(UserEvent, related_name="audited_logs")
    admin_item = models.ForeignKey(AdminEvent, related_name="audited_logs")
    time = models.DateTimeField(u'审核时间', auto_now_add=True)
    audit_result = models.BooleanField(default=False, verbose_name=u"审核结果")
    reason = models.CharField(u"备注（拒绝原因）", max_length=100,blank=True)
    def __unicode__(self):
        return u"审核员：%s,用户事件：%s，管理员事件:%s,审核结果：%s，审核时间：%s，提交时间：%s" % (self.user,self.item,
                        self.admin_item,self.audit_result, self.time, self.item.time)
    class Meta:
        ordering = ["-time",]
class TransList(models.Model):
    user = models.ForeignKey(MyUser, related_name="translist")
    time = models.DateTimeField(u'时间', auto_now_add=True)
    initAmount = models.IntegerField(u'变动前数值')
    transAmount = models.IntegerField(u'变动数值')
    reason = models.CharField(max_length=20, verbose_name=u"变动原因")
    remark = models.CharField(u"备注", max_length=100, blank=True)
    transType = models.CharField(max_length=2, choices=TRANS_TYPE, verbose_name=u"变动类型")
    user_event = models.ForeignKey(UserEvent, related_name="translist", null=True,on_delete=models.SET_NULL)
    admin_event = models.ForeignKey(AdminEvent, related_name="translist", null=True,on_delete=models.SET_NULL)
    def __unicode__(self):
        return u"%s:%s了%s现金 提交时间%s" % (self.user, self.get_transType_display(),self.transAmount,
                                       self.user_event.time if self.user_event else "")
    class Meta:
        ordering = ["-time",]

class ScoreTranlist(models.Model):
    user = models.ForeignKey(MyUser, related_name="score_translist")
    time = models.DateTimeField(u'时间', auto_now_add=True)
    initAmount = models.IntegerField(u'变动前数值')
    transAmount = models.IntegerField(u'变动数值')
    reason = models.CharField(max_length=20, verbose_name=u"变动原因")
    remark = models.CharField(u"备注", max_length=100,blank=True)
    transType = models.CharField(max_length=1, choices=TRANS_TYPE, verbose_name=u"变动类型")
    user_event = models.ForeignKey(UserEvent, related_name="score_translist", null=True,on_delete=models.SET_NULL)
    admin_event = models.ForeignKey(AdminEvent, related_name="score_translist", null=True,on_delete=models.SET_NULL)
    def __unicode__(self):
        return u"%s:%s了%s积分 提交时间%s" % (self.user, self.get_transType_display(),self.transAmount, self.time)
    class Meta:
        ordering = ['-time']

class ExchangeRecord(models.Model):
    tranlist = OneToOneField(ScoreTranlist, primary_key=True)
    commodity = models.ForeignKey(Commodity, related_name="exchange_record")
    name = models.CharField(u'收件人姓名', max_length=20)
    tel = models.CharField(u'收件人手机号', max_length=14)
    addr = models.CharField(u'收件人地址', max_length=100)
    postcode = models.CharField(u'邮编', max_length=10)
    message = models.CharField(u'留言', default=u"暂无", max_length=100)
    user_event = GenericRelation("UserEvent",related_query_name='exchangerecord')
    def __unicode__(self):
        return u"%s:收件人为 %s" % (self.tranlist.user, self.name)
    class Meta:
        ordering = ["-tranlist__time",]

class Press(Base):
    summary = models.TextField(verbose_name=u"摘要")
    type = models.CharField(u"新闻类型", max_length=1, choices=NEWS_TYPE)
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True,
                             verbose_name=u"新闻图片上传(110*72)")
    content=UEditorField(u"内容", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    #增加title、keywords、description等seo字段
    seo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
    seo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
    seo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
    def clean(self):
        if self.type == '3' and not self.pic:
            raise ValidationError({'pic': u'新闻类型必输'})
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"公告、攻略（关于我们）"
        verbose_name_plural = u"公告、攻略（关于我们）"
class Advertisement(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"banner图片上传(1920*300)，小于100k")
    location = models.CharField(u"广告位置", max_length=2, choices=ADLOCATION)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    navigation = models.CharField(u"banner导航文字", max_length=6)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"横幅广告-电脑端"
        verbose_name_plural = u"横幅广告-电脑端"
    def clean(self):
        if self.pic and self.pic.size > 100000:
            raise ValidationError({'pic': u'图片大小不能超过100k'})
class Advertisement_Mobile(Base):
    mpic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"移动端banner图片上传(414*160)，小于30k")
    location = models.CharField(u"广告位置", max_length=2, choices=ADLOCATION)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    navigation = models.CharField(u"banner导航文字", max_length=6)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"横幅广告-移动端"
        verbose_name_plural = u"横幅广告-移动端"
    def clean(self):
        if self.mpic and self.mpic.size > 30000:
            raise ValidationError({'mpic': u'图片大小不能超过30k'})
class MAdvert(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"banner图片上传(1920*300)，小于100k")
    location = models.CharField(u"广告位置", max_length=2, choices=MADLOCATION)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    navigation = models.CharField(u"banner导航文字", max_length=6)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"普通广告"
        verbose_name_plural = u"普通广告"
    def clean(self):
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
class MAdvert_App(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"banner图片上传(1920*300)，小于100k")
    location = models.CharField(u"广告位置", max_length=2, choices=MADLOCATION)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    wel_id = models.ForeignKey(Welfare, verbose_name="展示福利")
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"app今日推荐"
        verbose_name_plural = u"app今日推荐"
    def clean(self):
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
ADLOCATION_NEW = (
    ('00', u'首页banner（680*380）'),
    ('01', u'首页推荐位（200*200），配不超过20字的文字描述'),
    ('02', u'首页发现位（280*200），配不超过30字的文字描述'),
    ('03', u'首页中间广告位（1250*110）'),
    ('04', u'首页下面的广告位（870*110）'),
    ('10', u'红包页大banner（680*380）'),
    ('11', u'红包页小banner（275*185）'),
)
class MAdvert_PC(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"图片上传", help_text=u"保证图片质量的前提下，越小越好，莉萍负责图片 审核")
    location = models.CharField(u"位置", max_length=2, choices=ADLOCATION_NEW)
    description = models.CharField(u"文字描述", max_length=30, blank=True)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"PC端广告位（新）"
        verbose_name_plural = u"PC端广告位（新）"
    def clean(self):
        if self.pic:
            if self.location in ['00', '10', '03'] and self.pic.size > 100000:
                raise ValidationError({'pic': u'图片大小不能超过100k'})
            elif self.pic.size > 50000:
                raise ValidationError({'pic': u'图片大小不能超过50k'})
class UserWelfare(models.Model):
    user = models.ForeignKey(MyUser, related_name="submited_welfare")
    title = models.CharField(max_length=200, verbose_name=u"标题")
    url = models.CharField(u"福利地址",max_length=200)
    reason = models.CharField(u"推荐理由",max_length=200)
    date = models.DateTimeField(u"创建时间", auto_now_add=True)
    user_event = GenericRelation("UserEvent",related_query_name='submit_welfare_record')
    class Meta:
        ordering = ["-date"]
        unique_together = (('title', 'url'),)
    def __unicode__(self):
        return self.title + '+' + self.url
class Activity(Base):
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', blank=False,
                             verbose_name=u"banner图片上传(110*72)")
    summary = models.TextField(verbose_name=u"摘要")
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"热门活动"
        verbose_name_plural = u"热门活动"

class LotteryRecord(models.Model):
    user = models.ForeignKey(MyUser, related_name="lottery_record")
    award = models.CharField(u"奖品", max_length=20)
    date = models.DateTimeField(u"创建时间", auto_now_add=True, db_index=True)
    class Meta:
        ordering = ["-date"]
    def __unicode__(self):
        return u"%s中了%s" % (self.user, self.award)

class Information(Base):
    summary = models.TextField(verbose_name=u"摘要")
    type = models.CharField(u"资讯类型", max_length=10, choices=INFORMATION_TYPE)
    source = models.CharField(u"来源", max_length=10, default=u"挖福利")
    is_display = models.BooleanField(default=True, verbose_name=u"是否在列别页中显示")
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"图片上传(260*160)")
    content=UEditorField(u"内容", width=900, height=300, toolbars="full",
                         imagePath="photos/%(year)s/%(month)s/%(day)s/",
                         filePath="photos/%(year)s/%(month)s/%(day)s/",
                         upload_settings={"imageMaxSize":120000},settings={},command=None,blank=True)
    #增加title、keywords、description等seo字段
    seo_title = models.CharField(max_length=200, verbose_name=u"SEO标题", blank=True)
    seo_keywords = models.CharField(max_length=200, verbose_name=u"SEO关键词", blank=True)
    seo_description = models.CharField(max_length=200, verbose_name=u"SEO描述", blank=True)
    class Meta:
        ordering = ["-news_priority","-pub_date"]
        verbose_name = u"资讯"
        verbose_name_plural = u"资讯"
    def clean(self):
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})

class UserTask(models.Model):
    user = models.ForeignKey(MyUser)
    task = models.ForeignKey(Task)
    class Meta:
        unique_together = (('user', 'task'),)
    def __unicode__(self):
        return self.user.mobile + '+' + self.task.title


class Fuligou(models.Model):
    is_main = models.BooleanField()
    title = models.CharField(max_length=60)
    buy_price = models.FloatField()
    old_price = models.FloatField()
    img_src = models.CharField(max_length=200)
    href = models.CharField(max_length=200)
    def coupon_value(self):
        return self.old_price - self.buy_price
    def __unicode__(self):
        return self.title
    
class CreditCard(models.Model):
    title = models.CharField(u"名称", max_length=20)
    apply_num = models.IntegerField(u"申请人数")
    url = models.CharField(u"地址", max_length=200)
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）",blank=False)
    def clean(self):
        if self.pic and self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
    class Meta:
        verbose_name = u"信用卡"
        verbose_name_plural = u"信用卡"
class Loan(models.Model):
    title = models.CharField(u"名称", max_length=20)
    url = models.CharField(u"地址", max_length=200)
    class Meta:
        verbose_name = u"借点钱"
        verbose_name_plural = u"借点钱"
        
class MediaProject(models.Model):
    title = models.CharField(max_length=200, verbose_name=u"标题")
    pub_date = models.DateField(u"创建日期", default=timezone.now)
    state = models.CharField(u"项目状态", max_length=1, choices=STATE)
    is_vip_bonus = models.BooleanField(u'适用VIP奖励', default=True)
    is_multisub_allowed = models.BooleanField(u"是否允许同一手机号多次提交", default=False)
    is_need_screenshot = models.BooleanField(u'是否需要截图', default=True)
    attention = models.TextField(u'注意事项', max_length=500)
    user_event = GenericRelation("UserEvent",related_query_name='mediaproject')
    class Meta:
        verbose_name = u"媒体单项目"
        verbose_name_plural = u"媒体单项目"
    def __unicode__(self):
        return self.title