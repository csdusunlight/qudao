#coding:utf-8
from django.db import models
from wafuli.models import InvestLog, SUB_WAY
from django.utils import timezone
from account.models import MyUser
from decimal import Decimal

# Create your models here.

class IPLog(models.Model):
    investlog = models.OneToOneField(InvestLog, primary_key = True)
    time = models.DateTimeField(default=timezone.now)
    ip = models.CharField('remote_ip', max_length=15, db_index=True)
    user = models.ForeignKey(MyUser, related_name="iplogs")
    award = models.DecimalField(u'奖励金额', default = Decimal(0), max_digits=10, decimal_places=2)
    def __unicode__(self):
        return self.user.username + self.ip + ' ' +str(self.award)
    class Meta:
        ordering = ['-time']
        
class IPAward(models.Model):
    ip = models.CharField('remote_ip', max_length=15, db_index=True)
    date = models.DateField(u"日期")
    class Meta:
        index_together = ('ip','date') #联合索引
        
    
class SubmitRank(models.Model):
    user = models.OneToOneField(MyUser)
    rank = models.PositiveIntegerField(u"排名", default=100)
    sub_num = models.PositiveIntegerField(u"获得奖励数", default=0)
    award = models.IntegerField(u'奖励金额',  default=0)
    def __unicode__(self):
        return self.user.username +',' +str(self.award)+','+str(self.rank)
    class Meta:
        ordering = ['rank']