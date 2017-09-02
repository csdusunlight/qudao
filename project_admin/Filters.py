#coding:utf-8
'''
Created on 2017年7月3日

@author: lch
'''
import django_filters
from project_admin.models import Project, ProjectInvestData, \
    AccountBill, ProjectStatis
class ProjectFilter(django_filters.rest_framework.FilterSet):
    startDate = django_filters.DateFromToRangeFilter(name="time")
    finishdate = django_filters.DateFromToRangeFilter(name="finish_time")
    name__contains = django_filters.CharFilter(name="name", lookup_expr='contains')
    platformname__contains = django_filters.CharFilter(name="platform", lookup_expr='name__contains')
    class Meta:
        model = Project
        fields = ['id', 'platformname__contains', 'name__contains', 'startDate','state', 'contact', 'coopway', 'settleway',
                  'contract_company','finishdate']

class ProjectInvestDateFilter(django_filters.rest_framework.FilterSet):
    investtime = django_filters.DateFromToRangeFilter(name="invest_time")
    audittime = django_filters.DateTimeFromToRangeFilter(name="audit_time")
    name__contains = django_filters.CharFilter(name="project", lookup_expr='name__contains')
    class Meta:
        model = ProjectInvestData
        fields = ['is_futou', 'invest_time', 'project', 'name__contains', 'investtime','state', 'invest_mobile', 'audittime', 'source']
class ProjectStatisFilter(django_filters.rest_framework.FilterSet):
    dateft = django_filters.DateFromToRangeFilter(name="project__time")
    name__contains = django_filters.CharFilter(name="project", lookup_expr='name__contains')
    project_state = django_filters.CharFilter(name="project", lookup_expr='state')
    class Meta:
        model = ProjectStatis
        fields = ['project', 'name__contains', 'dateft','project_state' ]
        
class AccountBillFilter(django_filters.rest_framework.FilterSet):
    timeft = django_filters.DateTimeFromToRangeFilter(name="time")
    name__contains = django_filters.CharFilter(name="account", lookup_expr='name__contains')
    account_type = django_filters.CharFilter(name="account", lookup_expr='type')
    class Meta:
        model = AccountBill
        fields = ['type', 'account_type', 'subtype', 'name__contains', 'time','target','account']
        