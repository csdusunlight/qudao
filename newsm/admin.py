from django.contrib import admin

from .models import Tag, Article,Agroup,Url


class TagAdmin(admin.ModelAdmin):
    list_display = ( 'tintro',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ( 'agname',)

class UrlAdmin(admin.ModelAdmin):
    list_display = ( 'uname','url','upub_date')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('acontent','ais_published','ais_hot')
    list_filter = ['ais_published', 'ais_hot',]
    filter_horizontal = ('atag',)
    readonly_fields = ('aupdate_time',)
    #filter_overrides=('apic',)
#
#
admin.site.register(Tag, TagAdmin)
admin.site.register(Agroup, GroupAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Url,UrlAdmin)