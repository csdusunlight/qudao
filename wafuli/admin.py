#coding:utf-8
from django.contrib import admin
from wafuli.tools import batch_subscribe, batch_deletesub
from wafuli.models import *
class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('user','pub_date',)
    list_display = ('title','is_official','state','user','id')
    list_filter = ['is_official',]
    def save_model(self, request, obj, form, change):
        super(ProjectAdmin,self).save_model (request, obj, form, change)
        if not change:
            obj.user = request.user
            obj.save(update_fields=['user',])
        if obj.is_addedto_repo:
            if obj.state=='10' or obj.state=='20':
                batch_subscribe(request.user, True, obj)
        if obj.state=='30' or not obj.is_addedto_repo:
            batch_deletesub(obj)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Company)
admin.site.register(MAdvert_PC)
admin.site.register(Announcement)
admin.site.register(SubscribeShip)
admin.site.register(Mark)