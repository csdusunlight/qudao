from django.contrib import admin
# from .forms import MyUserChangeForm, MyUserCreationForm
from .models import *
# Register your models here.
class MyUserAdmin(admin.ModelAdmin):
# The forms to add and change user instances
#     form = MyUserChangeForm
#     add_form = MyUserCreationForm
    # The fields to be used in displaying the User model.
#     fieldsets = (
#         (None, {'fields': ('mobile','username','qq_number','password')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions', 'admin_permissions')}),
#         ('Important dates', {'fields': ('qq_name', 'type', 'level', 'profile', 'with_total','accu_income', 'date_joined', )}),
#         ('others', {'fields': ('balance', 'margin_account','domain_name', 'cs_qq')}),
#     )
#     add_fieldsets = (
#     (None, {
#             'classes': ('wide',),
#             'fields': ('mobile', 'username','qq_number','password1', 'password2')}
#             ),
#     )
    search_fields = ('nickName',)
#     ordering = ('mobile',)
    list_display = ('nickName','date_joined')
#     list_filter = ('is_staff', 'is_superuser', 'is_active')
#     filter_horizontal = ('groups', 'user_permissions', 'admin_permissions')
# Now register the new UserAdmin...
admin.site.register(App)
admin.site.register(WXUser, MyUserAdmin)

