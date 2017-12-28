from django.contrib import admin
from weixin.models import WeiXinUser, Reply_KeyWords

# Register your models here.
admin.site.register(WeiXinUser)
admin.site.register(Reply_KeyWords)