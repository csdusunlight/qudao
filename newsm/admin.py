from django.contrib import admin

from .models import Tag, Article,Agroup,Url


class TagAdmin(admin.ModelAdmin):
    list_display = ( 'tintro',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ( 'agname',)

class UrlAdmin(admin.ModelAdmin):
    list_display = ( 'uname','url','upub_date')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id','atitle','ais_published','ais_hot','aupdate_time','agroup__agname')
    list_filter = ['id','atitle','ais_published', 'ais_hot','aupdate_time','acontent','agroup_agname']
    filter_horizontal = ('atag',)
    readonly_fields = ('aupdate_time',)
    #filter_overrides=('apic',)
#
#
admin.site.register(Tag, TagAdmin)
admin.site.register(Agroup, GroupAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Url,UrlAdmin)