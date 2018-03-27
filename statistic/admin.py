from django.contrib import admin
from statistic.models import UserDetailStatis, UserAverageStatis
# from activity.models import SubmitRank

# Register your models here.
admin.site.register(UserDetailStatis)
admin.site.register(UserAverageStatis)
# admin.site.register(SubmitRank)