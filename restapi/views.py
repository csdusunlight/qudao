from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog
from wafuli.serializers import ProjectSerializer
from permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer
from account.models import MyUser
# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,IsAdmin)
class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

class ProjectDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
class UserList(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

class UserDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    
class InvestlogList(generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InvestLog.objects.all()
        else:
            return InvestLog.objects.filter(user=user)
    serializer_class = InvestLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
#     filter_fields = ['state',]
    pagination_class = MyPageNumberPagination

class InvestlogDetail(BaseViewMixin,generics.RetrieveUpdateDestroyAPIView):
    queryset = InvestLog.objects.all()
    serializer_class = InvestLogSerializer