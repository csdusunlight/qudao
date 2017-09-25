from django.contrib import admin
from statistic.models import UserDetailStatis, UserAverageStatis

# Register your models here.
admin.site.register(UserDetailStatis)
admin.site.register(UserAverageStatis)