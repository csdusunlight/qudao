#coding:utf-8
'''
Created on 2017年8月23日

@author: lch
'''
import django_filters
from wafuli.models import InvestLog, Project
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