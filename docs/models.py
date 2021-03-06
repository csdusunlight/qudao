#coding:utf-8
from django.db import models
from account.models import MyUser
from dragon.settings import FANSHU_DOMAIN
from public.models import RandomPrimaryIdModel
import datetime

# Create your models here.
class Document(RandomPrimaryIdModel):
    user = models.ForeignKey(MyUser, related_name="docs")
    title = models.CharField(u"标题", max_length=20, default=u"无标题")
    content = models.CharField(u"正文", max_length=1000000)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)
    view_count = models.IntegerField(u"浏览次数", default=0)
    is_on = models.BooleanField(u"开启/关闭", default=True)
    secret = models.CharField(u"密码", max_length=20, blank=True)
    is_star = models.BooleanField(u"标签", default=False)
    close_time = models.DateTimeField(u"定时关闭时间", null=True, blank=True)
    def __unicode__(self):
        return self.user.username + self.title
    def fanshu_url(self):
        return 'http://' + FANSHU_DOMAIN + '/docs/' + str(self.id)
    
class DocStatis(models.Model):
    date = models.DateField(default=datetime.date.today)
    doc = models.ForeignKey(Document, related_query_name = "docstatis")
    count = models.IntegerField(default=0)
    def __unicode__(self):
        return str(self.doc) + str(self.date)