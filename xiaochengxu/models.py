#coding:utf-8
from django.db import models
# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,PermissionsMixin
, BaseUserManager)
import datetime
from django.utils import timezone
from decimal import Decimal
from account.models import MyUser

class App(models.Model):
    user = models.ForeignKey(MyUser, related_name="apps")
    app_id = models.CharField(max_length=18, primary_key=True)
    app_secret = models.CharField(max_length=32)
    app_name = models.CharField(max_length=32)
    def __unicode__(self):
        return '%s:%s' % (self.app_name, self.app_id)
class WXUser(models.Model):
    openid = models.CharField(u'公众号关注者编号', max_length=30, unique=True)
    app = models.ForeignKey(App, related_name="wxusers")
    user = models.ForeignKey(MyUser, related_name="wxusers")
    nickName = models.CharField(u'微信昵称', max_length=30)
    date_joined = models.DateTimeField(u'注册时间', default=timezone.now)
    gender = models.CharField(u'性别', max_length=1)
    province = models.CharField(u'省', max_length=20)
    city = models.CharField(u'城市', max_length=20)
    country = models.CharField(u'国家', max_length=50)
    avatarUrl = models.CharField(u'头像', max_length=200, default='/static/images/user-icon.png')
    language = models.CharField(max_length=20)
    unionid = models.CharField(u'unionid', max_length=50,)
    balance = models.DecimalField(u'账户余额', default = Decimal(0), max_digits=10, decimal_places=2)
    zhifubao = models.CharField(u'收款信息', max_length=64, blank=True)
    mobile = models.CharField('mobile number', max_length=11)
    qq_number = models.CharField(u"QQ号", max_length=20)
    qq_name = models.CharField(u"QQ昵称", max_length=20)
    class Meta:
        verbose_name = 'wxuser'
        verbose_name_plural = 'wxusers'
        ordering = ['-date_joined']
class WXUserlogin(models.Model):
    wxuser = models.ForeignKey(WXUser, related_name="user_login_history")
    time = models.DateTimeField(u'登录时间', default = timezone.now)
    class Meta:
        ordering = ["-time"]
    def __unicode__(self):
        return self.user.mobile
