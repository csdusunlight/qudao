#coding:utf-8
from django.contrib import admin

# Register your models here.
from .models import *
from .tools import writeHtml,createUrl
from django.http.response import Http404

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
# Register your models here.
class NewsAdmin(admin.ModelAdmin):
#     fields = ('title', 'pic1', 'pic2', 'pic3', 'content', 'url')
    search_fields = ['title',]
    list_filter = ['news_priority', 'change_user',]
    def save_model(self, request, obj, form, change):
        obj.change_user = str(request.user)
#         if obj.advert is None:
#             obj.advert = Advertisement.objects.filter(location='7',is_hidden=False).first()
        obj.save()
class FinanceAdmin(NewsAdmin):
    readonly_fields = ('url','pub_date','change_user')
    filter_horizontal = ('marks',)
    list_display = ('title','state','news_priority')
    list_priority=('news_priority',)
#     def formfield_for_foreignkey(self, db_field, request, **kwargs): 
#         if db_field.name == "company": 
#             kwargs["queryset"] = Company.objects.order_by("pinyin") 
#         return super(FinanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    def save_model(self, request, obj, form, change):
        super(FinanceAdmin,self).save_model (request, obj, form, change)
        if not change:
            obj.url = reverse('finance_detail', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class TaskAdmin(NewsAdmin):
    readonly_fields = ('url','pub_date','change_user')
    list_display = ('title','is_forbidden',)
    list_filter = ['is_forbidden',]
    list_display = ('title','state',)
    def save_model(self, request, obj, form, change):
        super(TaskAdmin,self).save_model (request, obj, form, change)      
        if not change:
            obj.url = reverse('task_detail', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class CommodityAdmin(NewsAdmin):
    search_fields = ['name',]
    list_filter = []
    readonly_fields = ('url',)
    def save_model(self, request, obj, form, change):
        super(CommodityAdmin,self).save_model (request, obj, form, change)   
        if not change:
            obj.url = reverse('commodity_detail', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class ZeroAdmin(NewsAdmin):
    readonly_fields = ('url','pub_date','change_user')
    def save_model(self, request, obj, form, change):
        super(ZeroAdmin,self).save_model (request, obj, form, change) 
        if not change:
            obj.url = reverse('welfare', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class PressAdmin(NewsAdmin):
    readonly_fields = ('pub_date','change_user','url')
    def save_model(self, request, obj, form, change):
        obj.change_user = str(request.user)
        obj.save()
        if not change:
            obj.url = reverse('press_detail', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class ComAdmin(admin.ModelAdmin):
    search_fields = ['name', 'level','site','capital','address','launch_date','trusteeship','background',]
class UserEventAdmin(admin.ModelAdmin):
    raw_id_fields = ['user',]
    search_fields = ()
    list_display = ('user','content_object', 'invest_account','time','event_type','audit_state')
class AdminEventAdmin(admin.ModelAdmin):
    raw_id_fields = ['admin_user','custom_user']
class ActivityAdmin(admin.ModelAdmin):
#     fields = ('title', 'pic1', 'pic2', 'pic3', 'content', 'url')
    search_fields = ['title',]
    list_filter = ['news_priority', 'change_user',]
    def get_readonly_fields(self, request,obj=None):
        fields=[]
        if request.user.is_superuser:
            return fields
        else:  
            fields=['change_user']
            return fields  
class TransListAdmin(admin.ModelAdmin):
    search_fields = ['user__mobile',]
    raw_id_fields = ['user','user_event','admin_event']
class CouponAdmin(admin.ModelAdmin):
    list_display = ('project','user', 'exchange_code','is_used',)
    search_fields = ['user__mobile',]
class AdvertisementAdmin(admin.ModelAdmin):
    list_filter = ('location',)
admin.site.register(Finance,FinanceAdmin)
admin.site.register(Company, ComAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Commodity,CommodityAdmin)
admin.site.register(UserEvent, UserEventAdmin)
admin.site.register(AuditLog)
admin.site.register(AdminEvent,AdminEventAdmin)
admin.site.register(ScoreTranlist,TransListAdmin)
admin.site.register(TransList,TransListAdmin)
admin.site.register(ExchangeRecord)
admin.site.register(Press,PressAdmin)

admin.site.register(Coupon, CouponAdmin)
admin.site.register(Message)
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Advertisement_Mobile, AdvertisementAdmin)
admin.site.register(MAdvert, AdvertisementAdmin)
admin.site.register(MAdvert_App, AdvertisementAdmin)
admin.site.register(UserWelfare)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(LotteryRecord)

class WelfareAdmin(admin.ModelAdmin):
    search_fields = ['title',]
    list_filter = ['news_priority', 'state',]
    readonly_fields = ('pub_date','change_user','url')
    filter_horizontal = ('marks',)
    list_display = ('title','state',)
    def save_model(self, request, obj, form, change):
        obj.change_user = str(request.user)
#         if obj.advert is None:
#             obj.advert = Advertisement.objects.filter(location='7',is_hidden=False).first()
        super(WelfareAdmin,self).save_model (request, obj, form, change)
        if not change:
            obj.url = reverse('welfare', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
class HongbaoAdmin(WelfareAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.type = 'hongbao'
        super(HongbaoAdmin,self).save_model (request, obj, form, change)
class BaoyouAdmin(WelfareAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.type = 'baoyou'
        obj.change_user = str(request.user)
#         if obj.advert is None:
#             obj.advert = Advertisement.objects.filter(location='7',is_hidden=False).first()
        if not change:
            obj.save()
        obj.url = reverse('exp_welfare_openwindow') + '?id=' + str(obj.id) + "&type=Welfare"
        obj.save()
class CouponProjectAdmin(WelfareAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.type = 'youhuiquan'
        super(CouponProjectAdmin,self).save_model (request, obj, form, change)      
admin.site.register(Hongbao,HongbaoAdmin)
admin.site.register(CouponProject,CouponProjectAdmin)
admin.site.register(Baoyou,BaoyouAdmin)
admin.site.register(Welfare,WelfareAdmin)
admin.site.register(Mark)

class InformationAdmin(NewsAdmin):
    readonly_fields = ('pub_date','change_user','url')
    def save_model(self, request, obj, form, change):
        obj.change_user = str(request.user)
        obj.save()
        if not change:
            obj.url = reverse('information', kwargs={'id': obj.pk})
            obj.save(update_fields=['url',])
admin.site.register(Information,InformationAdmin)
admin.site.register(UserTask)
admin.site.register(Fuligou)
admin.site.register(CreditCard)
admin.site.register(Loan)
admin.site.register(MAdvert_PC)
admin.site.register(MediaProject)