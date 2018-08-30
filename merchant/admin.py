from django.contrib import admin
from merchant.models import Margin_Translog, Apply_Project,\
    MerchantProjectStatistics, ZhifubaoTransaction

# Register your models here.
admin.site.register(Margin_Translog,)
admin.site.register(Apply_Project,)
admin.site.register(MerchantProjectStatistics,)

class TRANSAdmin(admin.ModelAdmin):
    list_display = ('transNo', 'user', 'create_time','time','amount', 'remark')
    list_filter = ('remark',)



admin.site.register(ZhifubaoTransaction, TRANSAdmin)
