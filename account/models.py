#coding:utf-8
from django.db import models
from .tools import random_str
# Create your models here.
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
import datetime
from django.utils import timezone
from django.contrib.auth.hashers import (
    check_password, make_password,
)
from wafuli.data import BANK
from decimal import Decimal
import re
from django.core.exceptions import ValidationError
class MyUserManager(BaseUserManager):

    def _create_user(self, mobile, username, qq_number, password,
                     is_staff, is_superuser):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = datetime.datetime.now()
        if not mobile or not username or not qq_number:
            raise ValueError('The given qq, mobile and username must be set')
        user = self.model(mobile=mobile, username=username,qq_number=qq_number,
                          is_staff=is_staff,
                          is_active=True, is_superuser=is_superuser,
                          date_joined=now)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, username, qq_number, password=None, **extra_fields):
        return self._create_user(mobile, username, qq_number, password, False, False)

    def create_superuser(self, mobile, username, qq_number, password):
        return self._create_user(mobile, username, qq_number, password, True, True)
    def get_by_natural_key(self, username):
        try:
            return self.get(**{'mobile': username})
        except MyUser.DoesNotExist:
            return self.get(**{'username': username})

COLORS = (
    ('0', u'皮肤0'),
    ('1', u'皮肤1'),
    ('2', u'皮肤2'),
    ('3', u'皮肤3'),
    ('4', u'皮肤4'),
    ('5', u'皮肤5'),
)
USER_LEVEL = (
    ('01', u'一级代理'),
    ('02', u'二级代理'),
    ('03', u'三级代理'),
    ('04', u'四级代理'),
    ('05', u'五级代理'),
)
USER_ORIGIN = (
    ('1', u'学生党'),
    ('2', u'宝妈'),
    ('3', u'羊毛党'),
    ('4', u'兼职'),
    ('5', u'个人站长'),
    ('6', u'金融大Ｖ'),
    ('7', u'理财师'),
    ('8', u'理财推手'),

)
USER_EXP_YEAR = (
    ('1', u'新手'),
    ('2', u'1年之内'),
    ('3', u'1-2年'),
    ('4', u'3年以上'),
)
USER_CUSTOME_VOLUMN = (
    ('1', u'50人以下'),
    ('2', u'50到100人'),
    ('3', u'100人到500人'),
    ('4', u'500人'),
)
USER_FUNDS_VOLUMN = (
    ('1', u'50万以下'),
    ('2', u'50到100万'),
    ('3', u'100到500万'),
    ('4', u'500万'),
)
USER_INVEST_ORIENTATION = (
    ('1', u'小额量大单'),
    ('2', u'低息大额单'),
    ('3', u'短期高返单'),
    ('4', u'媒体单'),
)
IS_CHANNEL = (
    ('0', u'非渠道用户'),
    ('-1',u'审核中'),
    ('1', u'渠道用户'),
)


class MyUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField('email address', max_length=255)
    mobile = models.CharField('mobile number', max_length=11, unique=True,)
    username = models.CharField('username', max_length=30, unique=True)
    qq_number = models.CharField(u"QQ号", max_length=20, unique=True)
    qq_name = models.CharField(u"QQ昵称", max_length=20)
    date_joined = models.DateTimeField(u'注册时间', default=timezone.now)
    type = models.CharField(u'用户类型', default='agent',max_length=10)
    level = models.CharField(u"用户等级", choices=USER_LEVEL, default='03', max_length=2)
    domain_name = models.CharField(u"个人主页域名", max_length=20, unique=True)
    cs_qq = models.CharField(u"客服QQ号", max_length=20, blank=True)
    color = models.CharField(u'个人主页色调', choices=COLORS, default='0', max_length=2)
    submit_bg = models.CharField(u'交单页面背景', default='0', max_length=2)
    picture = models.ImageField(upload_to='photos/user_headphoto', verbose_name=u"个人头像")
    profile = models.TextField(u"个人简介", default=u"~~这个人啥都没写~~")
    qualification = models.CharField(u"资质证明截图", max_length=200)
    with_total = models.DecimalField(u'提现总额度', default = Decimal(0), max_digits=10, decimal_places=2)
    accu_income = models.DecimalField(u'累计收入', default = Decimal(0), max_digits=10, decimal_places=2)
    is_staff = models.BooleanField('staff status', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
        help_text=('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    balance = models.DecimalField(u'账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    admin_permissions = models.ManyToManyField('AdminPermission',
        verbose_name='admin permissions', blank=True,
        related_name="user_set", related_query_name="user")
    is_autowith = models.BooleanField(u'是否自动提现', default=False)
    is_book_email_notice = models.BooleanField(u'是否预约单邮件通知', default=True)
    margin_account = models.DecimalField(u'保证金账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    inviter = models.ForeignKey('self', related_name = 'invitees',
                                blank=True, null=True, on_delete=models.SET_NULL, default=None)
    invite_code = models.CharField(u"邀请码", blank=True, max_length=10)
    invite_settle = models.DecimalField(u'上月员工推广结算金额', default = Decimal(0), max_digits=10, decimal_places=2)
    
    zhifubao = models.CharField(u"支付宝账号（邮箱或手机号）", blank=True, max_length=50)
    zhifubao_real_name = models.CharField(u"支付宝实名", blank=True, max_length=20)

    is_channel = models.CharField(u"是否渠道", choices=IS_CHANNEL, default='0', max_length=2)  #
    num_message_sync = models.IntegerField(u"新消息数量",default='0')
    objects = MyUserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username','qq_number']
    def get_fanshu_domain(self):
        return 'http://%s.51fanshu.com' % self.domain_name
    def set_pay_password(self, raw_password):
        self.pay_password = make_password(raw_password)
    def check_pay_password(self, raw_password):
        return check_password(raw_password, self.pay_password)
#     def save(self, force_insert=False, force_update=False, using=None,
#         update_fields=None):
#         if not self.pk:
#             self.invite_code = random_str(5) + str(MyUser.objects.count())
#         return AbstractBaseUser.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    def get_full_name(self):
        return self.mobile
    def get_short_name(self):
        return self.mobile
    def get_abbre_name(self):
        username = self.username
        if len(username) > 4:
            username = username[0:4] + '****'
        else:
            username = username + '****'
        return username
    def has_admin_perms(self, code):
        return self.admin_permissions.filter(code=code).exists()
    def has_permission100(self):
        return self.has_admin_perms('100')
    def has_permission200(self):
        return self.has_admin_perms('200')
    def picture_url(self):
        """
        Returns the URL of the image associated with this Object.
        If an image hasn't been uploaded yet, it returns a stock image
        
        :returns: str -- the image url
        
        """
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        else:
            return '/static/images/user-icon.png'
        def __unicode__(self):
            return self.mobile
    def get_encrypt_mobile(self):
        mobile = self.mobile
        if len(mobile)>=7:
            return mobile[:3] + '****' + mobile[-4:]
        else:
            return mobile
    def clean(self):
        mat = re.match(r'[0-9a-zA-A\-_]+$', self.domain_name)
        if not mat:
            raise ValidationError({'pub_date': u'域名只能包含数字、字母、-和_字符'})
class BankCard(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_bankcard")
    card_number = models.CharField(u"银行卡号",max_length=23)
    real_name = models.CharField(u'实名', max_length=10)
    bank = models.CharField(u'开户银行', max_length=10, choices=BANK)
    subbranch = models.CharField(u'开户支行', max_length=50)
    def __unicode__(self):
        return self.user.mobile + self.get_bank_display() + self.real_name
class Userlogin(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_login_history")
    time = models.DateTimeField(u'登录时间', default = timezone.now)
    class Meta:
        ordering = ["-time"]
    def __unicode__(self):
        return self.user.mobile
class UserSignIn(models.Model):
    user = models.ForeignKey(MyUser, related_name="user_signin_history")
    date = models.DateField(u'签到日期', default = timezone.now)
    signed_conse_days = models.PositiveIntegerField("连续签到天数", default=1)
    class Meta:
        ordering = ["-date"]
        unique_together = (('user', 'date'),)
class MobileCode(models.Model):
    mobile = models.CharField('mobile number', max_length=11, )
    identifier = models.CharField('identifier', max_length=10, blank=True,)
    rand_code = models.CharField('random code', max_length=6)
    create_at = models.DateTimeField("created at", auto_now_add=True, editable=True)
    remote_ip = models.CharField('remote_ip', max_length=15, blank=True)
    def __unicode__(self):
        return self.identifier + ':' + self.mobile + ':' + self.remote_ip
    class Meta:
        ordering = ['-create_at']



class AdminPermission(models.Model):
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField('name', max_length=255)
    def __unicode__(self):
        return self.code + ',' + self.name

class UserToken(models.Model):
    token = models.CharField("token", max_length=32, primary_key=True)
    user = models.ForeignKey(MyUser,related_name = 'tokens',)
    expire = models.BigIntegerField(u"expire_time")


class DBlock(models.Model):
    index = models.CharField("name",max_length=10,primary_key=True)
    description = models.CharField("description",max_length=30)

AUDIT_STATE = (
    ('0', u'审核通过'),
    ('1', u'待审核'),
    ('2', u'审核未通过'),
)    
class ApplyLog(models.Model):
    mobile = models.CharField('mobile number', max_length=11, unique=True,)
    password = models.CharField('password', max_length=20, blank=False)
    username = models.CharField('username', max_length=30, unique=True)
    qq_number = models.CharField(u"QQ号", max_length=20, unique=True)
    qq_name = models.CharField(u"QQ昵称", max_length=20)
    profile = models.TextField(u"个人简介", default=u"~~这个人啥都没写~~")
    qualification = models.CharField(u"资质证明截图", max_length=200)
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    admin_user = models.ForeignKey(MyUser, related_name="applylog_admin", null=True)
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    level = models.SmallIntegerField(u"用户等级", choices=USER_LEVEL, default=2)
    inviter = models.ForeignKey(MyUser, related_name = 'invitees_applogs',
                                blank=True, null=True, on_delete=models.SET_NULL, default=None)
    class Meta:
        ordering = ["submit_time",]
    def __unicode__(self):
        return self.mobile

class ApplyLogForChannel(models.Model):
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    audit_time = models.DateTimeField(u'审核时间', null=True, blank=True)
    admin_user = models.ForeignKey(MyUser, related_name="applylogforchannel", null=True)
    user = models.ForeignKey(MyUser, related_name="applylog_custom")
    audit_reason = models.CharField(u"审核原因", max_length=30)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    user_origin = models.CharField(u"用户来源", choices=USER_ORIGIN, max_length=2)
    user_exp_year = models.CharField(u"用户经验年限", choices=USER_EXP_YEAR, max_length=2)
    user_custom_volumn = models.CharField(u"用户客户体量", choices=USER_CUSTOME_VOLUMN, max_length=2)
    user_funds_volumn = models.CharField(u"用户资金体量", choices=USER_FUNDS_VOLUMN, max_length=2)
    user_invest_orientation = models.CharField(u"用户投资去向", choices=USER_INVEST_ORIENTATION, max_length=2)

    class Meta:
        ordering = ["submit_time",]
    def __unicode__(self):
        return self.user.mobile

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