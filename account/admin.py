from django.contrib import admin
from .forms import MyUserChangeForm, MyUserCreationForm
from django.contrib.auth.admin import UserAdmin
from account.models import *
# Register your models here.
class MyUserAdmin(UserAdmin):
# The forms to add and change user instances
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    # The fields to be used in displaying the User model.
    fieldsets = (
        (None, {'fields': ('mobile','username','qq_number','password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'admin_permissions')}),
        ('Important dates', {'fields': ('qq_name', 'type', 'level', 'profile', 'with_total','accu_income', 'date_joined', )}),
        ('others', {'fields': ('balance',)}),
    )
    add_fieldsets = (
    (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'username','qq_number','password1', 'password2')}
            ),
    )
    search_fields = ('mobile','username','qq_number')
    ordering = ('mobile',)
    list_display = ('mobile', 'qq_number', 'username','is_staff','date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'type', 'level')
    filter_horizontal = ('groups', 'user_permissions', 'admin_permissions')
# Now register the new UserAdmin...
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(UserSignIn)
admin.site.register(Userlogin)
admin.site.register(MobileCode)
admin.site.register(AdminPermission)
admin.site.register(DBlock)
admin.site.register(BankCard)

