#coding:utf-8
'''
Created on 2017年8月23日

@author: lch
'''
import django_filters
from coupon.models import UserCoupon
class UserCouponFilter(django_filters.rest_framework.FilterSet):
    create = django_filters.DateFromToRangeFilter(name="create_date")
    user_mobile = django_filters.CharFilter(name="user", lookup_expr='mobile')
    contract_contains = django_filters.CharFilter(name="contract", lookup_expr='name__contains')
    class Meta:
        model = UserCoupon
#         exclude = ['invest_image', 'invest_date', 'audit_time']
        fields = ['create','user_mobile', 'contract_contains']
