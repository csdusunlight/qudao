from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement
from permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer,\
    TransListSerializer, NoticeSerializer, ProjectSerializer,\
    SubscribeShipSerializer, AnnouncementSerializer
from account.models import MyUser
from rest_framework.filters import SearchFilter,OrderingFilter
from restapi.permissions import IsOwnerOrStaff
from restapi.Filters import InvestLogFilter, SubscribeShipFilter
from django.db.models import Q
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
            return queryset.filter(Q(is_officail=True) | Q(user__id=user.id))
        
    serializer_class = ProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_fields = ['state','type','is_multisub_allowed','is_official']
    ordering_fields = ('state','pub_date')
    search_fields = ('title', 'introduction')
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        serializer.save(is_official=False)

class ProjectDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsOwnerOrStaff,)
    
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
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        is_official = project.is_official
        serializer.save(is_official=is_official)

class InvestlogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = InvestLog.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = InvestLogSerializer
    
class TranslistList(BaseViewMixin, generics.ListAPIView):
    queryset = TransList.objects.all()
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = TransListSerializer
    
class NoticeList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        return Notice.objects.filter(user=user)
    serializer_class = NoticeSerializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class NoticeDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class SubscribeShipList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        return Notice.objects.filter(user=user)
    queryset = SubscribeShip.objects.all()
    serializer_class = SubscribeShipSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = SubscribeShipFilter
    pagination_class = MyPageNumberPagination

class SubscribeShipDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.all()
        else:
            return InvestLog.objects.filter(user=user)
    serializer_class = SubscribeShipSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class AnnouncementList(BaseViewMixin, generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    
class AnnouncementDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsAdmin,)