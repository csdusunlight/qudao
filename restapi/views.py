from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog, TransList, Notice
from permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer,\
    TransListSerializer, NoticeSerializer, ProjectSerializer
from account.models import MyUser
from rest_framework.filters import SearchFilter,OrderingFilter
from restapi.permissions import IsOwnerOrStaff
from restapi.Filters import InvestLogFilter
# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,IsAdmin)
class ProjectList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = Project.objects.filter(state__in=['10','20'])
    serializer_class = ProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_fields = ['state','type','is_multisub_allowed']
    ordering_fields = ('state','pub_date')
    search_fields = ('title', 'introduction')
    pagination_class = MyPageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(is_official=False)

class ProjectDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
class UserList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

class UserDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class InvestlogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.all()
        else:
            return InvestLog.objects.filter(user=user)
    serializer_class = InvestLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = InvestLogFilter
    pagination_class = MyPageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        is_official = project.is_official
        serializer.save(is_official=is_official)

class InvestlogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.all()
        else:
            return InvestLog.objects.filter(user=user)
    serializer_class = InvestLogSerializer
    
class TranslistList(BaseViewMixin, generics.ListAPIView):
    queryset = TransList.objects.all()
    serializer_class = TransListSerializer
    
class NoticeList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        return Notice.objects.filter(user=user)
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class NoticeDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer