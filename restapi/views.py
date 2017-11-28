#coding:utf-8
from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement, WithdrawLog, Mark, Company, BookLog
from permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer,\
    TransListSerializer, NoticeSerializer, ProjectSerializer,\
    SubscribeShipSerializer, AnnouncementSerializer, DayStatisSerializer,\
    ApplyLogSerializer, WithdrawLogSerializer, UserDetailStatisSerializer,\
    UserAverageStatisSerializer, MarkSerializer, CompanySerializer,\
    RankSerializer, IPLogSerializer, BookLogSerializer, DocumentSerializer
from account.models import MyUser, ApplyLog
from rest_framework.filters import SearchFilter,OrderingFilter
from restapi.permissions import IsOwnerOrStaff, IsSelfOrStaff
from restapi.Filters import InvestLogFilter, SubscribeShipFilter, UserFilter,\
    ApplyLogFilter, TranslistFilter, WithdrawLogFilter
from django.db.models import Q
from wafuli_admin.models import DayStatis
from statistic.models import UserDetailStatis, UserAverageStatis
from rest_framework.exceptions import ValidationError
from activity.models import SubmitRank, IPLog
from docs.models import Document
import re
# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
class ProjectList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.filter(state__in=['10','20'], )
        if user.is_staff:
            return queryset
        else:
            return queryset.filter(Q(is_official=True) | Q(user__id=user.id))
        
    serializer_class = ProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_fields = ['state','type','is_multisub_allowed','is_official']
    ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('title', 'introduction')
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        obj = serializer.save(is_official=False, user=self.request.user, state='10')
        SubscribeShip.objects.create(project=obj, user=self.request.user)

class ProjectDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class UserList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = UserFilter
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

class UserDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrStaff,)
    def perform_update(self, serializer):
        domain_name = serializer.validated_data.get('domain_name', None)
        if domain_name:
            mat = re.match(r'[0-9a-zA-A\-_]+$', domain_name)
            if not mat:
                raise ValidationError({'detail': u'域名只能包含数字、字母、-和_字符'})
        generics.RetrieveUpdateDestroyAPIView.perform_update(self, serializer)
    
class InvestlogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.all()
        else:
            return InvestLog.objects.filter(user=user)
    serializer_class = InvestLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('submit_time',)
    filter_class = InvestLogFilter
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        is_official = project.is_official
        invest_mobile = serializer.validated_data['invest_mobile']
        if not project.is_multisub_allowed:
            if project.company is None:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
            else:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
            if queryset.exclude(audit_state='2').exists():    
                raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save(is_official=is_official, audit_state='1', user=self.request.user)

class InvestlogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = InvestLog.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = InvestLogSerializer
    def perform_update(self, serializer):
        if serializer.validated_data.has_key('project'):
            project = serializer.validated_data['project']
            id = serializer.instance.id
            invest_mobile = serializer.validated_data['invest_mobile']
            if not project.is_multisub_allowed:
                if project.company is None:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
                else:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
                if queryset.exclude(id=id).exclude(audit_state='2').exists():
                    raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save()
    
class TranslistList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TransList.objects.all()
        else:
            return TransList.objects.filter(user=user)
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = TransListSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = TranslistFilter
    
    
class NoticeList(BaseViewMixin, generics.ListCreateAPIView):
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('state', 'priority')
    serializer_class = NoticeSerializer
    pagination_class = MyPageNumberPagination
    def get_queryset(self):
        user = self.request.user
        return Notice.objects.filter(user=user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class NoticeDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class SubscribeShipList(BaseViewMixin, generics.ListAPIView):
    queryset = SubscribeShip.objects.all()
    def get_queryset(self):
        user = self.request.user
        return SubscribeShip.objects.filter(user=user)
    serializer_class = SubscribeShipSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('is_on','project__state')
    filter_class = SubscribeShipFilter
    pagination_class = MyPageNumberPagination

class SubscribeShipDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscribeShip.objects.all()
    serializer_class = SubscribeShipSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class AnnouncementList(BaseViewMixin, generics.ListCreateAPIView):
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('state', 'priority')
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    pagination_class = MyPageNumberPagination
    
class AnnouncementDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsAdmin,)
    
class DayStatisList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = DayStatis.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = DayStatisSerializer
    pagination_class = MyPageNumberPagination
    
class ApplyLogList(BaseViewMixin, generics.ListAPIView):
    queryset = ApplyLog.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = ApplyLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = ApplyLogFilter
    pagination_class = MyPageNumberPagination
    
    
class WithdrawLogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return WithdrawLog.objects.all()
        else:
            return WithdrawLog.objects.filter(user=user)
    serializer_class = WithdrawLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = WithdrawLogFilter
    pagination_class = MyPageNumberPagination

class UserDetailStatisList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserDetailStatis.objects.all()
        else:
            return UserDetailStatis.objects.filter(user=user)
    serializer_class = UserDetailStatisSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_fields = ('user', 'date')
    
class UserAverageStatisList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserAverageStatis.objects.all()
        else:
            return UserAverageStatis.objects.filter(user=user)
    serializer_class = UserAverageStatisSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_fields = ('user')

class MarkList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return Mark.objects.filter(user=self.request.user)
    serializer_class = MarkSerializer
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        if Mark.objects.filter(user=user).count() >= 7:
            return ValidationError({'detail':u"自建标签数目最多为7"})
        generics.ListCreateAPIView.perform_create(self, serializer)
class MarkDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Mark.objects.filter(user=self.request.user)
    serializer_class = Mark
    permission_classes = (IsOwnerOrStaff,)
class CompanyList(BaseViewMixin, generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = MyPageNumberPagination
class RankList(BaseViewMixin, generics.ListAPIView):
    permission_classes = ()
    queryset = SubmitRank.objects.all()
    serializer_class = RankSerializer
    pagination_class = MyPageNumberPagination
class IPLogList(BaseViewMixin, generics.ListAPIView):
    permission_classes = (IsAdmin,)
    queryset = IPLog.objects.all()
    serializer_class = IPLogSerializer
    pagination_class = MyPageNumberPagination
class BookLogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return BookLog.objects.filter(user=self.request.user)
    serializer_class = BookLogSerializer
    pagination_class = MyPageNumberPagination
class BookLogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return BookLog.objects.filter(user=self.request.user)
    serializer_class = BookLogSerializer
    permission_classes = (IsOwnerOrStaff,)
class DocumentList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = MyPageNumberPagination
class DocumentDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsOwnerOrStaff,)