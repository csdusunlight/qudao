from django.contrib import admin
from activity.models import IPLog, IPAward

# Register your models here.
admin.site.register(IPLog)
admin.site.register(IPAward)