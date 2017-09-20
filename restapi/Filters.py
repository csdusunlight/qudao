#coding:utf-8
'''
Created on 2017年8月23日

@author: lch
'''
import django_filters
from wafuli.models import InvestLog, Project, SubscribeShip
from account.models import MyUser, ApplyLog
# class ProjectInvestDateFilter(django_filters.rest_framework.FilterSet):
#     investtime = django_filters.DateFromToRangeFilter(name="invest_time")
#     audittime = django_filters.DateTimeFromToRangeFilter(name="audit_time")
#     name__contains = django_filters.CharFilter(name="project", lookup_expr='ti__contains')
#     class Meta:
#         model = Project
class InvestLogFilter(django_filters.rest_framework.FilterSet):
    investtime = django_filters.DateFromToRangeFilter(name="invest_date")
    audittime = django_filters.DateFromToRangeFilter(name="audit_time")
    project_title_contains = django_filters.CharFilter(name="project", lookup_expr='title__contains')
    class Meta:
        model = InvestLog
        exclude = ['invest_image', 'invest_date', 'audit_time']
#         fields = ['event_type','audittime', 'project_title_contains', 'investtime','audit_state', 'invest_account', 'mobile']

class SubscribeShipFilter(django_filters.rest_framework.FilterSet):
    username = django_filters.CharFilter(name="user", lookup_expr='username')
    project_title_contains = django_filters.CharFilter(name="project", lookup_expr='title__contains')
    class Meta:
        model = SubscribeShip
        fields = '__all__'


class UserFilter(django_filters.rest_framework.FilterSet):
    join_date = django_filters.DateFromToRangeFilter(name="date_joined")
    class Meta:
        model = MyUser
        fields = ['mobile', 'username', 'qq_name', 'qq_number', 'join_date']
        
class ApplyLogFilter(django_filters.rest_framework.FilterSet):
    submit_date = django_filters.DateFromToRangeFilter(name="submit_time")
    audit_date = django_filters.DateFromToRangeFilter(name="audit_time")
    admin_user_mobile = django_filters.CharFilter('admin_user', lookup_expr='mobile')
    class Meta:
        model = ApplyLog
        fields = ['mobile', 'qq_name', 'qq_number', 'submit_date', 'audit_date',
                  'audit_state', 'admin_user_mobile']