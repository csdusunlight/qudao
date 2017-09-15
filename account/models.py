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
    ('1', u'蓝色'),
    ('2', u'红色'),
)   
class MyUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField('email address', max_length=255)
    mobile = models.CharField('mobile number', max_length=11, unique=True,)
    username = models.CharField('username', max_length=30, unique=True)
    qq_number = models.CharField(u"QQ号", max_length=20, unique=True)
    qq_name = models.CharField(u"QQ昵称", max_length=20)
    date_joined = models.DateTimeField(u'注册时间', default=timezone.now)
    type = models.CharField(u'用户类型', default='agent',max_length=10)
    level = models.SmallIntegerField(u"用户等级", default=2)
    color = models.CharField(u'个人主页色调', choices=COLORS, default='1', max_length=2)
    picture = models.ImageField(upload_to='photos/user_headphoto', verbose_name=u"个人头像")
    profile = models.TextField(u"个人简介", default=u"~~这个人啥都没写~~")
    qualification = models.CharField(u"资质证明截图", max_length=200)
    with_total = models.DecimalField(u'提现总额度', default = Decimal(0), max_digits=10, decimal_places=2)
    accu_income = models.DecimalField(u'累计收入', default = Decimal(0), max_digits=10, decimal_places=2)
    inviter = models.ForeignKey('self', related_name = 'invitees',
                                blank=True, null=True, on_delete=models.SET_NULL)
    invite_code = models.CharField(u"邀请码", unique=True, blank=True, max_length=20)
    is_staff = models.BooleanField('staff status', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
        help_text=('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    
    invite_balance = models.DecimalField(u'邀请奖励账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    invite_income = models.DecimalField(u'邀请奖励现金', default = Decimal(0), max_digits=10, decimal_places=2)
    balance = models.DecimalField(u'账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    admin_permissions = models.ManyToManyField('AdminPermission',
        verbose_name='admin permissions', blank=True,
        related_name="user_set", related_query_name="user")
    objects = MyUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username','qq_number']

    def set_pay_password(self, raw_password):
        self.pay_password = make_password(raw_password)
    def check_pay_password(self, raw_password):
        return check_password(raw_password, self.pay_password)
    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        if not self.pk:
            self.invite_code = random_str(5) + str(MyUser.objects.count())
        return AbstractBaseUser.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
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
    def __unicode__(self):
        return self.mobile


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
    code = models.CharField(unique=True, max_length=3)
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

