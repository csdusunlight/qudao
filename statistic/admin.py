from django.contrib import admin
from statistic.models import UserDetailStatis, UserAverageStatis,\
    PerformanceStatistics
# from activity.models import SubmitRank

# Register your models here.
admin.site.register(UserDetailStatis)
admin.site.register(UserAverageStatis)
admin.site.register(PerformanceStatistics)