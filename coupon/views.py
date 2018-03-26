#coding:utf-8
from django.shortcuts import render, redirect
from rest_framework.generics import ListCreateAPIView
from coupon.serializers import UserCouponSerializer, ContractSerializer
from coupon.models import UserCoupon, Contract
from public.Paginations import MyPageNumberPagination
from public.permissions import CsrfExemptSessionAuthentication
from rest_framework import permissions
from rest_framework.filters import SearchFilter
import django_filters
from public.tools import has_permission
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from account.models import MyUser
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger('wafuli')
# Create your views here.
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
class contractList(BaseViewMixin, ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Contract.objects.all()
        else:
            return Contract.objects.filter(user=user)
        
    serializer_class = ContractSerializer
    filter_backends = (SearchFilter,)
#     filter_class = ApplyProjectFilter
#     ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('name', )
    pagination_class = MyPageNumberPagination
class userCouponList(BaseViewMixin, ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserCoupon.objects.all()
        else:
            return UserCoupon.objects.filter(user=user)
        
    serializer_class = UserCouponSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ['user']
#     filter_class = ApplyProjectFilter
#     ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('name', )
    pagination_class = MyPageNumberPagination
    
