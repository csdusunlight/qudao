from django.contrib import admin
from merchant.models import Margin_Translog, Apply_Project,\
    MerchantProjectStatistics, ZhifubaoTransaction

# Register your models here.
admin.site.register(Margin_Translog,)
admin.site.register(Apply_Project,)
admin.site.register(MerchantProjectStatistics,)
admin.site.register(ZhifubaoTransaction,)
