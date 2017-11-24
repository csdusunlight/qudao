#coding:utf-8
from django.db import models
from account.models import MyUser

# Create your models here.
class WeiXinUser(models.Model):
    user = models.ForeignKey(MyUser, null=True, related_name="weixin_users")
    openid = models.CharField(u'公众号关注者编号', max_length=30, unique=True)
    nickname = models.CharField(u'微信昵称', max_length=30)
    sex = models.CharField(u'性别', max_length=1)
    province = models.CharField(u'省', max_length=20)
    city = models.CharField(u'城市', max_length=20)
    country = models.CharField(u'国家', max_length=50)
    headimgurl = models.CharField(u'头像', max_length=200)
    unionid = models.CharField(u'unionid', max_length=50, )