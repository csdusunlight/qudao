#coding:utf-8
'''
Created on 2017年8月23日

@author: lch
'''
import django_filters
from wafuli.models import UserEvent
class UserEventFilter(django_filters.rest_framework.FilterSet):
    investtime = django_filters.DateFromToRangeFilter(name="invest_time")
    audittime = django_filters.DateTimeFromToRangeFilter(name="audit_time")
    project_title_contains = django_filters.CharFilter(name="mediaproject", lookup_expr='title__contains')
    username = django_filters.CharFilter(name="user", lookup_expr='username')
    mobile = django_filters.CharFilter(name="user", lookup_expr='mobile')
    class Meta:
        model = UserEvent
        fields = ['event_type','audittime', 'project_title_contains', 'investtime','audit_state', 'invest_account', 'mobile']