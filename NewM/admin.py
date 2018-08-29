from django.contrib import admin

from .models import Tag2, Article2


class TagAdmin(admin.ModelAdmin):
    list_display = ( 'tslug', 'tintro',)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('Acontent','Acontent1')
#
#
admin.site.register(Tag2, TagAdmin)
admin.site.register(Article2, ArticleAdmin)