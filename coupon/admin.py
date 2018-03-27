from django.contrib import admin
from coupon.models import UserCoupon, Contract

# Register your models here.
admin.site.register(UserCoupon)
admin.site.register(Contract)