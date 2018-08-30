#coding:utf-8
from django.contrib import admin
from wafuli.tools import batch_subscribe, batch_deletesub
from wafuli.models import *
from public.pinyin import PinYin

class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('user','pub_date','pinyin','szm')
    list_display = ('title','is_official','category','is_addedto_repo','state','user','id')
    list_filter = ['is_official', 'is_addedto_repo', 'category']
    search_fields = ['title',]
    def save_model(self, request, obj, form, change):
        admin.ModelAdmin.save_model(self, request, obj, form, change)
        if not change:
            obj.user = request.user
            obj.save(update_fields=['user',])
        if obj.is_addedto_repo:
            if obj.state=='10' or obj.state=='20':
                batch_subscribe(request.user, True, obj)
        if obj.state=='30' or not obj.is_addedto_repo:
            batch_deletesub(obj)
        if obj.state != '10' and obj.doc and obj.doc.is_on:
            obj.doc.is_on = False
            obj.doc.save(update_fields=['is_on',])
        if obj.state == '10' and obj.doc and not obj.doc.is_on:
            obj.doc.is_on = True
            obj.doc.save(update_fields=['is_on',])
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name',]

admin.site.register(Project, ProjectAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(MAdvert_PC)
admin.site.register(Announcement)
admin.site.register(SubscribeShip)
admin.site.register(Mark)
admin.site.register(InvestLog)
admin.site.register(BookLog)


import os
# Create your tests here.
if __name__ == '__main__':
    pyin = PinYin()
    pyin.load_word()
    print pyin.hanzi2pinyin_split(u"激流卡")