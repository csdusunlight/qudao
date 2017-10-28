#coding:utf-8
from django.db import models
from wafuli.models import InvestLog, SUB_WAY
from django.utils import timezone
from account.models import MyUser

# Create your models here.

class IPLog(models.Model):
    investlog = models.OneToOneField(InvestLog, primary_key = True)
    time = models.DateTimeField(default=timezone.now)
    ip = models.CharField('remote_ip', max_length=15, db_index=True)
    user = user = models.ForeignKey(MyUser, related_name="iplogs")
    def __unicode__(self):
        return self.user.username + self.ip
    class Meta:
        ordering = ['-time']
        
class IPAward(models.Model):
    ip = models.CharField('remote_ip', max_length=15, db_index=True)
    date = models.DateField(u"日期")
    class Meta:
        index_together = ('ip','date') #联合索引