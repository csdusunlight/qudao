#coding:utf-8
from django.db import models
from account.models import MyUser

# Create your models here.
class Document(models.Model):
    user = models.ForeignKey(MyUser, related_name="docs")
    title = models.CharField(u"标题", max_length=20)
    content = models.CharField(u"正文", max_length=10000)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)
    def __unicode__(self):
        return self.user.username + self.title