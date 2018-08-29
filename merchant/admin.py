from django.contrib import admin
from merchant.models import Margin_Translog, Apply_Project,\
    MerchantProjectStatistics, ZhifubaoTransaction
from .models import Article5

# Register your models here.
admin.site.register(Margin_Translog,)
admin.site.register(Apply_Project,)
admin.site.register(MerchantProjectStatistics,)

class TRANSAdmin(admin.ModelAdmin):
    list_display = ('transNo', 'user', 'create_time','time','amount', 'remark')
    list_filter = ('remark',)


class Article4Admin(admin.ModelAdmin):
    list_display = ('Acontent','Acontent1')

admin.site.register(ZhifubaoTransaction, TRANSAdmin)
admin.site.register(Article5, Article4Admin)