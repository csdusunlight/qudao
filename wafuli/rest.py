#coding:utf-8
'''
Created on 2017年8月22日

@author: lch
'''
from rest_framework import generics, permissions
import django_filters
from Paginations import ProjectPageNumberPagination
from wafuli.models import Project
from wafuli.serializers import ProjectSerializer
from wafuli.permissions import CsrfExemptSessionAuthentication, IsAdmin
# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,IsAdmin)
class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_fields = ['state',]
    pagination_class = ProjectPageNumberPagination

class ProjectDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer    
# class UserEventList(BaseViewMixin,generics.ListCreateAPIView):
#     queryset = UserEvent.objects.all()
#     serializer_class = UserEventSerializer
#     filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_class = UserEventFilter
#     pagination_class = ProjectPageNumberPagination
#     
# class UserEventDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
#     queryset = UserEvent.objects.all()
#     serializer_class = UserEventSerializer