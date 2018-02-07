#coding:utf-8
'''
Created on 2018年1月16日

@author: lch
'''
import django_filters
from account.models import MyUser
from merchant.models import Apply_Project, Margin_Translog, Margin_AuditLog

class ApplyProjectFilter(django_filters.rest_framework.FilterSet):
    qq_number = django_filters.CharFilter('user', lookup_expr='qq_number')
    qq_name = django_filters.CharFilter('user', lookup_expr='qq_name__contains')
    submittime = django_filters.DateFromToRangeFilter(name="submit_time")
    audittime = django_filters.DateTimeFromToRangeFilter(name="audit_time")
    auditdate = django_filters.DateFromToRangeFilter(name="audit_time")
    project_title_contains = django_filters.CharFilter(name="project", lookup_expr='title__contains')
    user_mobile = django_filters.CharFilter(name="user", lookup_expr='mobile')
    user_level = django_filters.CharFilter(name="user", lookup_expr='level')
    project_state = django_filters.CharFilter(name="project", lookup_expr='state')
    class Meta:
        model = Apply_Project
        exclude = ['submit_time', 'audit_time']
#         fields = ['event_type','audittime', 'project_title_contains', 'investtime','audit_state', 'invest_account', 'mobile']


class TranslogFilter(django_filters.rest_framework.FilterSet):
    trans_date = django_filters.DateFromToRangeFilter(name="time")
    user_mobile = django_filters.CharFilter('user', lookup_expr='mobile')
    user_name = django_filters.CharFilter('user', lookup_expr='username')
    reason_contains = django_filters.CharFilter('reason', lookup_expr='contains')
    class Meta:
        model = Margin_Translog
        fields = ['user_mobile', 'user_name', 'reason_contains', 'trans_date', 'transType']

class MarginAuditLogFilter(django_filters.rest_framework.FilterSet):
    submit_date = django_filters.DateFromToRangeFilter(name="submit_time")
    audit_date = django_filters.DateFromToRangeFilter(name="audit_time")
    user_mobile = django_filters.CharFilter('user', lookup_expr='mobile')
    qq_number = django_filters.CharFilter('user', lookup_expr='qq_number')
    user_name = django_filters.CharFilter('user', lookup_expr='username')
    user_level = django_filters.CharFilter('user', lookup_expr='level')
    admin_mobile = django_filters.CharFilter('admin_user', lookup_expr='mobile')
    card_number = django_filters.CharFilter('user', lookup_expr='user_bankcard__card_number')
    real_name = django_filters.CharFilter('user', lookup_expr='user_bankcard__real_name')
    class Meta:
        model = Margin_AuditLog
        fields = ['submit_date', 'audit_date', 'user_mobile', 'qq_number','user_name', 'audit_state', 'card_number', 'real_name', 'type']