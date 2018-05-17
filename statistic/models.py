#coding:utf-8
from django.db import models
from account.models import MyUser
import datetime

# Create your models here.
def get_today_date():
    return datetime.date.today()

#用与个人中心首页统计
class UserDetailStatis(models.Model):
    user = models.ForeignKey(MyUser, related_query_name="user_detail_statis")
    date = models.DateField(u"日期", default=get_today_date)
    settle_amount = models.DecimalField(u'结算数值', max_digits=10, decimal_places=2)
    item_count = models.IntegerField(u"结算条目数量",default=0)
    project_count = models.IntegerField(u"结算项目数量",default=0)
    invest_amount = models.DecimalField(u'投资额', max_digits=10, decimal_places=2)
    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d") + self.user.username
    class Meta:
        unique_together = (('user', 'date'),)
        ordering = ['-date',]
    
class UserAverageStatis(models.Model):
    user = models.ForeignKey(MyUser, related_query_name="user_avag_statis")
    settle_amount_average = models.DecimalField(u'平均结算数值', max_digits=10, decimal_places=2)
    item_count_average = models.FloatField(u"平均结算条目数量",default=0)
    def __unicode__(self):
        return self.user.username

#用于绩效统计
class PerformanceStatistics(models.Model):
    startdate = models.DateField(u"统计起始日期")
    enddate = models.DateField(u"统计截止日期")
    user = models.ForeignKey(MyUser, related_query_name="perfoms")
    amount = models.DecimalField(u'绩效金额', max_digits=10, decimal_places=2)
    def __unicode__(self):
        return self.user.username + ' ' + str(self.amount)