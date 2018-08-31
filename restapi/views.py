#coding:utf-8
from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from public.Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement, WithdrawLog, Mark, Company, BookLog
from public.permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer,\
    TransListSerializer, NoticeSerializer, ProjectSerializer,\
    SubscribeShipSerializer, AnnouncementSerializer, DayStatisSerializer,\
    ApplyLogSerializer, WithdrawLogSerializer, UserDetailStatisSerializer,\
    UserAverageStatisSerializer, MarkSerializer, CompanySerializer,\
    BookLogSerializer, DocumentSerializer, MesssageSerializer,\
    PerformStatisSerializer, ProjectSerializerForAdmin
from account.models import MyUser, ApplyLog, Message
from rest_framework.filters import SearchFilter,OrderingFilter
from public.permissions import IsOwnerOrStaff, IsSelfOrStaff
from restapi.Filters import InvestLogFilter, SubscribeShipFilter, UserFilter,\
    ApplyLogFilter, TranslistFilter, WithdrawLogFilter, ProjectFilter
from django.db.models import Q
from wafuli_admin.models import DayStatis
from statistic.models import UserDetailStatis, UserAverageStatis,\
    PerformanceStatistics
from rest_framework.exceptions import ValidationError
# from activity.models import SubmitRank, IPLog
from docs.models import Document
import re
from django.http import JsonResponse

# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
class ProjectList(BaseViewMixin, generics.ListCreateAPIView):
    permission_classes = ()
    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.all()
        if user.is_staff:
            return queryset
        else:
            return queryset.filter(Q(is_official=True) | Q(user__id=user.id)).filter(state__in=['10','20'], )
        
    def get_serializer_class(self):
        if self.request.user.is_authenticated() and self.request.user.is_staff:
            return ProjectSerializerForAdmin
        return ProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = ProjectFilter
#     filter_fields = ['state','type','is_multisub_allowed','is_official','category']
    ordering_fields = ('state','pub_date','pinyin','current_state_date','points')
    search_fields = ('title','company__name')
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        obj = serializer.save(is_official=False, category='self', is_addedto_repo=False, user=self.request.user, state='10')
        SubscribeShip.objects.create(project=obj, user=self.request.user)

class ProjectDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class UserList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = UserFilter
    ordering_fields = ('margin_account','accu_income','balance')
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

from restapi.serializers import ApplyLogForChannelSerializer,ApplyLogForFangdanSerializer
from restapi.Filters  import ApplyLogForChannelFilter,ApplyLogForFangdanFilter
from account.models import ApplyLogForChannel,ApplyLogForFangdan
class ApplyLogForChannelList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = ApplyLogForChannel.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = ApplyLogForChannelSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = ApplyLogForChannelFilter
    ordering_fields = ('submit_time','audit_time')
    ordering = ('-submit_time')
    pagination_class = MyPageNumberPagination
    def get_queryset(self):#如果是查询已拒绝用户，那么用is_channle=0 和审批未通过字段为空
        user = self.request.user
        if user.is_staff:
            return ApplyLogForChannel.objects.all()
        else:
            return ApplyLogForChannel.objects.filter(user=user)

class ApplyLogForFangdanList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = ApplyLogForFangdan.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = ApplyLogForFangdanSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_class = ApplyLogForFangdanFilter
    ordering_fields = ('submit_time','audit_time')
    ordering = ('-submit_time')
    pagination_class = MyPageNumberPagination
    def get_queryset(self):#如果是查询已拒绝用户，那么用is_channle=0 和审批未通过字段为空
        user = self.request.user
        if user.is_staff:
            return ApplyLogForFangdan.objects.all()
        else:
            return ApplyLogForFangdan.objects.filter(user=user)

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
        category = project.category
        invest_mobile = serializer.validated_data['invest_mobile']
        if not project.is_multisub_allowed:
            if project.company is None:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
            else:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
            if queryset.exclude(audit_state='2').exists():    
                raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save(is_official=is_official, category=category, audit_state='1', user=self.request.user)

class InvestlogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = InvestLog.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = InvestLogSerializer
    def perform_update(self, serializer):
        if serializer.validated_data.has_key('invest_mobile'):
            project = serializer.instance.project
            submit_type = serializer.instance.submit_type
            id = serializer.instance.id
            invest_mobile = serializer.validated_data['invest_mobile']
            if not project.is_multisub_allowed or submit_type=='1':
                if project.company is None:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
                else:
                    queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
                if queryset.exclude(id=id).exclude(audit_state='2').exists():
                    raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save()
    def perform_destroy(self, instance):
        if instance.preaudit_state == '0' or instance.audit_state == '0':
            raise ValidationError({'detail':u"该数据正在审核中，无法删除"})
        generics.RetrieveUpdateDestroyAPIView.perform_destroy(self, instance)
    
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
    permission_classes = ()
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
class CompanyList2(BaseViewMixin, generics.ListAPIView):
    permission_classes = ()
    queryset = Company.objects.filter(project__state='10',project__is_official=True,
                                      project__is_addedto_repo=True).distinct()
    serializer_class = CompanySerializer
    pagination_class = MyPageNumberPagination
# class RankList(BaseViewMixin, generics.ListAPIView):
#     permission_classes = ()
#     queryset = SubmitRank.objects.all()
#     serializer_class = RankSerializer
#     pagination_class = MyPageNumberPagination
# class IPLogList(BaseViewMixin, generics.ListAPIView):
#     permission_classes = (IsAdmin,)
#     queryset = IPLog.objects.all()
#     serializer_class = IPLogSerializer
#     pagination_class = MyPageNumberPagination
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
        return Document.objects.filter(user=self.request.user).order_by("-update_time")
    serializer_class = DocumentSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('title',)
class DocumentDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = (IsOwnerOrStaff,)

from restapi.Filters import MessageFilter
class MessageList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return Message.objects.filter(user=self.request.user)
    serializer_class = MesssageSerializer
    filter_class = MessageFilter
    filter_backends = (SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    ordering_fields = ('time')
    search_fields = ('title','content')
    ordering = ('-time')


class MessageDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MesssageSerializer
    queryset = Message.objects.all()
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Message.objects.all()
        else:
            return Message.objects.filter(user=user)
    def partial_update(self,serializer,*args,**kwargs):
        Mid=kwargs['pk']
        para = self.request.data.get("isread",-1)
        if para =='1' and Mid != -1:
            objmsgs = self.queryset.filter(id=Mid) #.filter(user=self.request.user)
            if objmsgs.exists():
                objmsg=objmsgs[0]
                objmsg.is_read=True
                objmsg.save(update_fields=['is_read',])
                returndict ={"code":0}
                return JsonResponse(returndict)
            else:
                raise Exception("没有目标邮件！")
        else:
            raise Exception("传入参数错误!")





class PerformStatisList(BaseViewMixin, generics.ListAPIView):
    queryset = PerformanceStatistics.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = PerformStatisSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('user__username', )
