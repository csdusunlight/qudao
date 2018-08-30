from django.contrib import admin

from .models import Tag, Article,Agroup


class TagAdmin(admin.ModelAdmin):
    list_display = ( 'tintro',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ( 'agname',)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('acontent',)
    filter_horizontal = ('atag',)
    readonly_fields = ('aupdate_time',)
    #filter_overrides=('apic',)
#
#
admin.site.register(Tag, TagAdmin)
admin.site.register(Agroup, GroupAdmin)
admin.site.register(Article, ArticleAdmin)