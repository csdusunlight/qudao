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
    ('3', u'复审'),
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
    logo = models.ImageField(u"网站logo（120*50）", upload_to='logo/%Y/%m/%d')
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
    url = models.URLField(u"本页面地址",max_length=200)
    def is_new(self):
        now = datetime.datetime.now()
        days = (now-self.pub_date).days
        return days == 0
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.title

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
    title = models.CharField(max_length=20, verbose_name=u"标题")
    priority = models.IntegerField(u"优先级",default=3)
    pub_date = models.DateTimeField(u"创建时间", default=timezone.now)
    user = models.ForeignKey(MyUser, null=True, related_name="created_projects")
    is_official = models.BooleanField(u"是否官方项目", default=False)
    is_addedto_repo = models.BooleanField(u"是否加入项目库", default=True)
    is_book = models.BooleanField(u"是否需要预约", default=False)
    state = models.CharField(u"项目状态", max_length=2, choices=Project_STATE, default='10')
    pic = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name=u"标志图片上传（最大不超过30k，越小越好）", blank=True)
    strategy = models.URLField(u"攻略链接")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, verbose_name=u"合作平台")
    type = models.CharField(u"项目类别", max_length=1, choices=Project_TYPE, blank=True)
    is_multisub_allowed = models.BooleanField(u"是否允许同一手机号多次提交", default=False)
    introduction = models.TextField(u"项目简介",max_length=100,blank=True)
    price01 = models.CharField(u"一级代理价格",max_length=25, blank=True)
    price02 = models.CharField(u"二级代理价格",max_length=25, blank=True)
    price03 = models.CharField(u"三级代理价格",max_length=25, blank=True)
    cprice = models.CharField(u"客户指导价",max_length=40)
    shortprice = models.CharField(u"客户指导价简洁展示",max_length=20, help_text=u"格式必须为投资xxxx返xx，如投资1000返10")
    term = models.CharField(u"标期长度", max_length=20)
    investrange = models.CharField(u"投资额度区间", max_length=20)
    intrest = models.CharField(u"预期年化", max_length=20)
    necessary_fields = models.CharField(u"必填字段", max_length=50,help_text=u"投资用户名(0)，投资金额(1)，投资标期(2)，投资日期(3)，\
                支付宝信息(4)，投资手机号(5)，预期返现金额(6)，QQ号(7)，投资截图(8)，字段以英文逗号隔开，如0,1,2,3,4,5", default = '0,1,2,3,4,5')
    subscribers = models.ManyToManyField(MyUser, through='SubscribeShip')
    points = models.IntegerField(u"参与人数", default=0)
    channel = models.CharField(u"项目来源（上游渠道）", max_length=20, blank=True)
    up_price = models.CharField(u"结算价格（收入）", max_length=40, blank=True)
    pinyin = models.CharField(u"拼音全拼", max_length=100)
    szm = models.CharField(u"首字母", max_length=20)
    remark = models.CharField(u"项目备注", max_length=50, blank=True)
    def clean(self):
        if not self.pic:
            raise ValidationError({'pic': u'图片不能为空'})
        elif self.pic.size > 30000:
            raise ValidationError({'pic': u'图片大小不能超过30k'})
    class Meta:
        verbose_name = u"理财项目"
        verbose_name_plural = u"理财项目"
        ordering = ["-priority", "-pub_date"]
    def is_expired(self):
        return self.state != '10'
#     def marks_list(self):
#         mark_list = []
#         for mark in self.marks.all():
#             mark_list.append(mark.name)
#         return '|'.join(mark_list)
    def is_new(self):
        now = datetime.datetime.now()
        days = (now-self.pub_date).days
        return days == 0
    def picture_url(self):
        """
        Returns the URL of the image associated with this Object.
        If an image hasn't been uploaded yet, it returns a stock image
        
        :returns: str -- the image url
        
        """
        if self.company and self.company.logo:
            return self.company.logo.url
        elif self.pic and hasattr(self.pic, 'url'):
            return self.pic.url
        else:
            return ''
        def __unicode__(self):
            return self.mobile
    def __unicode__(self):
        return self.title
    
class SubscribeShip(models.Model):
    user = models.ForeignKey(MyUser)
    project = models.ForeignKey(Project)
    introduction = models.CharField(u"项目简介",max_length=100)
    myprice = models.CharField(u"保留字段",max_length=40)
    price = models.CharField(u"客户价",max_length=40)
    shortprice = models.CharField(u"客户价简洁展示",max_length=20,)
    is_on = models.BooleanField(u"是否在主页显示",default=True)
    is_recommend = models.BooleanField(u"是否放到推荐位置",default=False)
    intrest = models.CharField(u"预期年化", max_length=20)
    def get_project_price(self):
        level = self.user.level
        return getattr(self.project, 'price'+str(level))
    def __unicode__(self):
        return self.user.mobile + self.project.title
    class Meta:
        unique_together = (('user', 'project'),)
        ordering = ['project__state', "-project__priority", "-project__pub_date",]
class Mark(models.Model):
    user = models.ForeignKey(MyUser, null=True, related_name="created_marks")
    name = models.CharField(max_length=4, verbose_name=u"标签名",)
    subids = models.ManyToManyField(SubscribeShip, related_name="marks", verbose_name=u"sub ids", blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u"标签"
        verbose_name_plural = u"标签"
        unique_together = (('user', 'name'),)
SUB_TYPE = (
    ('1', u'首投'),
    ('2', u'复投'),
)
SUB_WAY = (
    ('1', u'主页提交'),
    ('2', u'逐条提交'),
    ('3', u'表格提交'),
    ('4', u'移动端自助提交'),
)
class InvestLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="investlog_submit")
    project = models.ForeignKey(Project, related_name="investlogs")
    submit_type = models.CharField(max_length=10, choices=SUB_TYPE, verbose_name=u"首投/复投")
    submit_way = models.CharField(max_length=10, choices=SUB_WAY, verbose_name=u"提交入口")
    is_official = models.BooleanField(u'是否官方项目',)
    is_selfsub = models.BooleanField(u'是否渠道用户自己提交的',default=False)
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    invest_mobile = models.CharField(u"投资手机号", max_length=11)
    invest_name = models.CharField(u"投资用户名/姓名0", max_length=11, blank=True)
    invest_amount = models.DecimalField(u'投资金额1', max_digits=10, decimal_places=2, blank=True, null=True)
    invest_term = models.IntegerField(u"投资标期2", blank=True, null=True)
    invest_date = models.DateField(u'投资日期(3)', default=get_today, blank=True)
    invest_image = models.CharField(u"投资截图(8)", max_length=1000, blank=True)
    qq_number = models.CharField(u"QQ号(7)", max_length=20, blank=True)
    zhifubao = models.CharField(u'支付宝账号4', max_length=64, blank=True)
    zhifubao_name = models.CharField(u'支付宝姓名', max_length=30, blank=True)
    expect_amount = models.CharField(u'用户预期返现金额(6)', max_length=20, blank=True)
    admin_user = models.ForeignKey(MyUser, related_name="investlog_admin", null=True)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    audit_reason = models.CharField(u"审核原因", max_length=30, blank=True)
    settle_amount = models.DecimalField(u'结算金额', max_digits=10, decimal_places=2, default=0)
    return_amount = models.DecimalField(u'返现金额', max_digits=10, decimal_places=2, null=True)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    def __unicode__(self):
        return u"来自渠道用户：%s 的投资数据提交：%s" % (self.user, self.invest_amount)
    class Meta:
        ordering = ["-submit_time",]
    def get_other_and_remark(self):
        ret = []
        if self.qq_number:
            ret.append(u"QQ：" + self.qq_number)
        if self.expect_amount:
            ret.append(u"预期返现：" + self.expect_amount)
        if self.remark:
            ret.append(u"备注：" + self.remark)
        return '|'.join(ret)
    def get_encrypt_mobile(self):
        mobile = self.invest_mobile
        if len(mobile)>=7:
            return mobile[:3] + '****' + mobile[-4:]
        else:
            return mobile
    def get_project_price(self):
        level = self.user.level
        return getattr(self.project, 'price'+str(level))

STATE = (
    ('0', u'置顶'),
    ('1', u'普通'),
)     
class Notice(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_notice")
    content = models.CharField(u"通知内容", max_length=100)
    time = models.DateTimeField(u"创建时间", default=timezone.now)
    priority = models.IntegerField(u"优先级",default=1)
    state = models.CharField(u"状态", choices=STATE, default='1', max_length=1)
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
    
    def balance(self):
        if self.transType == '0':
            return self.initAmount + self.transAmount
        else:
            return self.initAmount - self.transAmount

class WithdrawLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="withdrawlog")
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    amount = models.DecimalField(u'提现数值', max_digits=10, decimal_places=2)
    admin_user = models.ForeignKey(MyUser, related_name="withdrawlog_admin", null=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    class Meta:
        ordering = ["submit_time","-amount"]
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
    location = models.CharField(u"位置", choices=ADLOCATION_NEW, max_length=100)
    description = models.CharField(u"文字描述", max_length=30, blank=True)
    is_hidden = models.BooleanField(u"是否隐藏",default=False)
    class Meta:
        ordering = ["-priority","-pub_date"]
        verbose_name = u"PC端广告位（新）"
        verbose_name_plural = u"PC端广告位（新）"
    def clean(self):
        if self.pic and self.pic.size > 100000:
                raise ValidationError({'pic': u'图片大小不能超过100k'})


class Announcement(models.Model):
    content = models.CharField(u"通知内容", max_length=100)
    time = models.DateTimeField(u"创建时间", default=timezone.now)
    priority = models.IntegerField(u"优先级",default=1)
    state = models.CharField(u"状态", choices=STATE, default='1', max_length=1)
    def __unicode__(self):
        return self.content
    class Meta:
        verbose_name = u"个人中心的通知"
        verbose_name_plural = u"个人中心的通知"
        ordering = ['-priority', '-time']
        
BOOK_STATE = (
    ('0', u'预约成功'),
    ('1', u'未处理'),
    ('2', u'作废'),
    ('3', u'延后处理'),
)    
class BookLog(models.Model):
    user = models.ForeignKey(MyUser, related_name="booklogs")
    project = models.ForeignKey(Project, related_name="booklogs")
    submit_time = models.DateTimeField(u"提交时间", default=timezone.now)
    book_date = models.DateField(u'预约日期')
    book_term = models.CharField(u'预约标期',max_length=10)
    book_content = models.CharField(u"预约明细", max_length=50)
    qq_number = models.CharField(u"QQ号", max_length=15, blank=True)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    state = models.CharField(max_length=10, choices=BOOK_STATE, verbose_name=u"预约状态")
    def __unicode__(self):
        return u"项目：" + self.project.title + '\n' \
            + u"QQ：" + self.qq_number + '\n' \
            + u"预约金额：" + self.book_content + '\n' \
            + u"预约标期：" + self.book_term + '\n' \
            + u"预约日期：" + str(self.book_date) + '\n' \
            + u"留言：" + self.remark
    class Meta:
        ordering = ['-submit_time']